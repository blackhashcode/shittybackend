from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import User, Event, Ticket, Payment, CashPayment, bKashPayment, PaymentContext
from .serializers import UserSerializer, EventSerializer, TicketSerializer, PaymentSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        """Override update to handle user update."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to handle user deletion."""
        user = self.get_object()
        # You can add any extra deletion logic for related objects if needed
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class IsOrganizer(IsAuthenticated):
    def has_permission(self, request, view):
        if request.user.role == 'organizer':  # Only organizers can create events
            return True
        raise PermissionDenied("You must be an organizer to create events.")


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        """Filter events based on query parameters."""
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        date = self.request.query_params.get('date')
        if category:
            queryset = queryset.filter(category=category)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    def perform_create(self, serializer):
        """Create event with VIP and Normal ticket limits."""
        organizer = self.request.user
        if organizer.role != 'organizer':
            raise PermissionDenied("Only organizers can create events.")
        
        event = serializer.save(organizer=organizer)

    def update(self, request, *args, **kwargs):
        """Override update to handle event update."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to handle event deletion."""
        event = self.get_object()
        # You can add extra deletion logic for related objects if needed (e.g., tickets)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(detail=False, methods=['post'])
    def purchase(self, request):
        """Purchase a ticket for an event."""
        data = request.data
        ticket = Ticket.objects.create(
            ticket_id=data.get('ticket_id'),
            event_id=data.get('event_id'),
            buyer_id=request.user.id,
            ticket_type=data.get('ticket_type'),
            price=data.get('price'),
            status='booked'
        )
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        """Override update to handle ticket update."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to handle ticket deletion."""
        ticket = self.get_object()
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        """Process a payment for a ticket."""
        amount = request.data.get('amount')
        method = request.data.get('method')

        if not amount or not method:
            return Response({"error": "Amount and method are required"}, status=400)

        if method == 'cash':
            strategy = CashPayment()
        elif method == 'bkash':
            strategy = bKashPayment()
        else:
            return Response({"error": "Invalid payment method"}, status=400)

        payment_context = PaymentContext(strategy)
        payment_context.execute_payment(amount)

        # After processing, create the payment record in the database
        payment = Payment.objects.create(
            payment_id='some_unique_id',  # You might want to generate a unique ID here
            amount=amount,
            method=method,
            status='Completed'
        )

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=201)
