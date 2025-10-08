from django.shortcuts import render
from django.http import HttpResponse
from .permissions import IsAdministrator, CanManageCards
from .models import Card, IDCardPrintLog, IDCardVerificationLog
from .serializers import (
    CardSerializer, CardCreateSerializer, CardUpdateSerializer, 
    CardListSerializer, StudentWithoutCardSerializer
)
from .pdf_service import IDCardPDFGenerator
from students.models import Student
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import logging

logger = logging.getLogger(__name__)


class PassthroughRenderer(BaseRenderer):
    """
    Return data as-is. View should supply a Response.
    """
    media_type = '*/*'
    format = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class CardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cards to be viewed or edited.
    
    Permissions:
    - Administrators: Full CRUD access to all card operations
    - Registration Officers: Can view, create, and manage cards
    """
    queryset = Card.objects.all().select_related('student').order_by('-created_at')
    serializer_class = CardSerializer
    permission_classes = [CanManageCards]
    lookup_field = 'card_uuid'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'student__department', 'student__student_status']
    search_fields = [
        'rfid_number', 'student__first_name', 'student__surname', 
        'student__registration_number', 'student__department'
    ]
    ordering_fields = ['created_at', 'issued_date', 'student__surname', 'rfid_number']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action == 'create':
            return CardCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CardUpdateSerializer
        elif self.action == 'list':
            return CardListSerializer
        return CardSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ['destroy']:
            # Only administrators can delete cards
            permission_classes = [IsAdministrator]
        else:
            # Both administrators and registration officers can access other actions
            permission_classes = [CanManageCards]
            
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a new card for a student.
        Available to both Administrators and Registration Officers.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Card creation initiated by {user_info}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        card = serializer.save()
        
        logger.info(f"Card created successfully by {user_info}: {card.card_uuid} for student {card.student.registration_number}")
        
        # Return detailed card information
        response_serializer = CardSerializer(card)
        response_data = response_serializer.data
        
        # Add creator info to response for audit trail
        response_data['created_by'] = {
            'username': request.user.username,
            'user_type': request.user.user_type,
            'full_name': getattr(request.user, 'full_name', request.user.username)
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        List all cards with pagination and filtering.
        Available to both Administrators and Registration Officers.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add user context and summary statistics to response
        if hasattr(response, 'data') and isinstance(response.data, dict):
            total_cards = Card.objects.count()
            active_cards = Card.objects.filter(is_active=True).count()
            inactive_cards = total_cards - active_cards
            
            response.data['summary'] = {
                'total_cards': total_cards,
                'active_cards': active_cards,
                'inactive_cards': inactive_cards
            }
            
            response.data['user_permissions'] = {
                'current_user': request.user.username,
                'user_type': request.user.user_type,
                'can_create': True,
                'can_modify': True,
                'can_deactivate': True,
                'can_delete': request.user.user_type == 'administrator'
            }
        
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single card record with full details.
        Available to both Administrators and Registration Officers.
        """
        response = super().retrieve(request, *args, **kwargs)
        
        # Add user permissions to the response
        if response.status_code == status.HTTP_200_OK:
            response.data['user_permissions'] = {
                'can_modify': True,
                'can_deactivate': True,
                'can_delete': request.user.user_type == 'administrator'
            }
        
        return response

    def update(self, request, *args, **kwargs):
        """
        Update card record - Available to both user types.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Card update initiated by {user_info}")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update card record - Available to both user types.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Card partial update initiated by {user_info}")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete card record - Only available to Administrators.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.warning(f"Card deletion initiated by {user_info}")
        
        instance = self.get_object()
        student_info = f"{instance.student.first_name} {instance.student.surname} ({instance.student.registration_number})"
        
        response = super().destroy(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logger.warning(f"Card {instance.card_uuid} for student {student_info} deleted by {user_info}")
        
        return response

    @action(
        detail=True, 
        methods=['patch'], 
        url_path='deactivate',
        permission_classes=[CanManageCards]
    )
    def deactivate_card(self, request, card_uuid=None):
        """
        Deactivate a card (set is_active to False).
        Available to both Administrators and Registration Officers.
        """
        card = self.get_object()
        
        if not card.is_active:
            return Response(
                {'detail': 'Card is already deactivated.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        card.is_active = False
        card.save(update_fields=['is_active', 'updated_at'])
        
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Card {card.card_uuid} deactivated by {user_info}")
        
        serializer = CardSerializer(card)
        return Response({
            'message': 'Card deactivated successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(
        detail=True, 
        methods=['patch'], 
        url_path='activate',
        permission_classes=[CanManageCards]
    )
    def activate_card(self, request, card_uuid=None):
        """
        Activate a card (set is_active to True).
        Available to both Administrators and Registration Officers.
        """
        card = self.get_object()
        
        if card.is_active:
            return Response(
                {'detail': 'Card is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        card.is_active = True
        card.save(update_fields=['is_active', 'updated_at'])
        
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Card {card.card_uuid} activated by {user_info}")
        
        serializer = CardSerializer(card)
        return Response({
            'message': 'Card activated successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(
        detail=False, 
        methods=['get'], 
        url_path='students-without-cards',
        permission_classes=[CanManageCards]
    )
    def students_without_cards(self, request):
        """
        Get list of students who don't have cards yet.
        Available to both Administrators and Registration Officers.
        """
        # Get students who don't have cards and are active
        students_without_cards = Student.objects.filter(
            is_active=True,
            card__isnull=True
        ).order_by('surname', 'first_name')
        
        # Apply search if provided
        search = request.query_params.get('search', '')
        if search:
            students_without_cards = students_without_cards.filter(
                Q(first_name__icontains=search) |
                Q(surname__icontains=search) |
                Q(registration_number__icontains=search) |
                Q(department__icontains=search)
            )
        
        # Apply department filter if provided
        department = request.query_params.get('department', '')
        if department:
            students_without_cards = students_without_cards.filter(
                department__icontains=department
            )
        
        serializer = StudentWithoutCardSerializer(students_without_cards, many=True)
        
        return Response({
            'count': students_without_cards.count(),
            'students': serializer.data,
            'message': f'Found {students_without_cards.count()} students without cards.'
        }, status=status.HTTP_200_OK)

    @action(
        detail=False, 
        methods=['get'], 
        url_path='statistics',
        permission_classes=[CanManageCards]
    )
    def card_statistics(self, request):
        """
        Get comprehensive card statistics.
        Available to both Administrators and Registration Officers.
        """
        total_students = Student.objects.filter(is_active=True).count()
        total_cards = Card.objects.count()
        active_cards = Card.objects.filter(is_active=True).count()
        inactive_cards = total_cards - active_cards
        students_without_cards = Student.objects.filter(
            is_active=True,
            card__isnull=True
        ).count()
        
        # Cards by department
        from django.db.models import Count
        cards_by_department = Card.objects.values(
            'student__department'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent cards (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_cards = Card.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        return Response({
            'summary': {
                'total_students': total_students,
                'total_cards': total_cards,
                'active_cards': active_cards,
                'inactive_cards': inactive_cards,
                'students_without_cards': students_without_cards,
                'coverage_percentage': round((total_cards / total_students * 100), 2) if total_students > 0 else 0,
                'recent_cards_30_days': recent_cards
            },
            'cards_by_department': cards_by_department,
            'user_info': {
                'current_user': request.user.username,
                'user_type': request.user.user_type,
                'generated_at': timezone.now().isoformat()
            }
        }, status=status.HTTP_200_OK)

    @action(
        detail=False, 
        methods=['post'], 
        url_path='bulk-create',
        permission_classes=[CanManageCards]
    )
    def bulk_create_cards(self, request):
        """
        Create cards for multiple students at once.
        Available to both Administrators and Registration Officers.
        """
        student_uuids = request.data.get('student_uuids', [])
        generate_rfid = request.data.get('generate_rfid', True)
        
        if not student_uuids:
            return Response(
                {'detail': 'student_uuids list is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_cards = []
        errors = []
        
        for student_uuid in student_uuids:
            try:
                student = Student.objects.get(student_uuid=student_uuid, is_active=True)
                
                # Check if student already has a card
                if hasattr(student, 'card'):
                    errors.append({
                        'student_uuid': student_uuid,
                        'error': f'Student {student.first_name} {student.surname} already has a card.'
                    })
                    continue
                
                # Generate RFID number
                if generate_rfid:
                    import random
                    import string
                    while True:
                        rfid_number = ''.join(random.choices(string.digits, k=10))
                        if not Card.objects.filter(rfid_number=rfid_number).exists():
                            break
                
                    # Create card
                    card = Card.objects.create(
                        student=student,
                        rfid_number=rfid_number
                    )
                    created_cards.append(card)
                
            except Student.DoesNotExist:
                errors.append({
                    'student_uuid': student_uuid,
                    'error': 'Student not found or inactive.'
                })
            except Exception as e:
                errors.append({
                    'student_uuid': student_uuid,
                    'error': str(e)
                })
        
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Bulk card creation by {user_info}: {len(created_cards)} cards created, {len(errors)} errors")
        
        # Serialize created cards
        serializer = CardListSerializer(created_cards, many=True)
        
        return Response({
            'success': True,
            'message': f'Created {len(created_cards)} cards, {len(errors)} errors.',
            'created_cards': serializer.data,
            'errors': errors,
            'summary': {
                'total_requested': len(student_uuids),
                'successful': len(created_cards),
                'failed': len(errors)
            },
            'created_by': {
                'username': request.user.username,
                'user_type': request.user.user_type,
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['get', 'post'],
        url_path='print-card',
        permission_classes=[CanManageCards],
        renderer_classes=[PassthroughRenderer]
    )
    def print_card(self, request, card_uuid=None):
        """
        Generate PDF for ID card printing.
        Available to both Administrators and Registration Officers.
        """
        try:
            card = self.get_object()
            student = card.student
            
            # Generate PDF
            pdf_generator = IDCardPDFGenerator(student, card)
            pdf_buffer = pdf_generator.generate()
            
            # Log the print action
            IDCardPrintLog.objects.create(
                card=card,
                student=student,
                printed_by=request.user.username,
                user_type=request.user.user_type,
                pdf_generated=True
            )
            
            user_info = f"{request.user.username} ({request.user.user_type})"
            logger.info(f"ID card PDF generated for {student.registration_number} by {user_info}")
            
            # Return PDF as download
            response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="ID_Card_{student.registration_number}.pdf"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating ID card PDF: {str(e)}")
            return Response(
                {'success': False, 'error': f'Failed to generate ID card PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_student(request, student_uuid):
    """
    Public endpoint to verify student details via QR code or direct link.
    Returns minimal student information for verification purposes.
    """
    try:
        student = Student.objects.get(student_uuid=student_uuid, is_active=True)
        
        # Check if student has a card
        has_card = hasattr(student, 'card') and student.card is not None
        
        # Log the verification
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        IDCardVerificationLog.objects.create(
            student=student,
            ip_address=ip_address,
            user_agent=user_agent,
            verification_source='qr_scan'
        )
        
        # Build photo URL if exists
        photo_url = None
        if hasattr(student, 'photo') and student.photo and student.photo.photo:
            photo_url = request.build_absolute_uri(student.photo.photo.url)
        
        # Return only necessary information for ID card verification
        verification_data = {
            'success': True,
            'verified': True,
            'student': {
                'registration_number': student.registration_number,
                'full_name': f"{student.first_name} {student.surname} {student.middle_name or ''}".strip(),
                'department': student.department,
                'program': "BACHELOR OF ENGINEERING",  # You may want to add this to student model
                'class_code': student.soma_class_code,
                'status': student.student_status,
                'academic_status': student.academic_year_status,
                'photo_url': photo_url,
                'has_card': has_card,
                'card_active': student.card.is_active if has_card else False,
            },
            'verified_at': timezone.now().isoformat(),
            'institution': 'DAR ES SALAAM INSTITUTE OF TECHNOLOGY'
        }
        
        logger.info(f"Student verification: {student.registration_number} from IP {ip_address}")
        
        return Response(verification_data, status=status.HTTP_200_OK)
        
    except Student.DoesNotExist:
        logger.warning(f"Failed verification attempt for UUID: {student_uuid}")
        return Response({
            'success': False,
            'verified': False,
            'message': 'Student not found or inactive.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error during verification: {str(e)}")
        return Response({
            'success': False,
            'verified': False,
            'message': 'Verification failed.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
