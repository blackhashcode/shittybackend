from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


# User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)

    # Add unique related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Custom related_name to avoid clash
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Custom related_name to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username


# Singleton Pattern: Ticket Configuration
class TicketConfig(models.Model):
    max_tickets_per_user = models.PositiveIntegerField(default=5)
    default_ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=50.0)

    class Meta:
        verbose_name = "Ticket Configuration"

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance, created = cls.objects.get_or_create(id=1)
        return cls._instance


# Event Model
# Event Model (Optional Update)
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('concert', 'Concert'),
        ('party', 'Party'),
        ('show', 'Show'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events', limit_choices_to={'role': 'organizer'})
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.PositiveIntegerField()  # Total available tickets
    available_vip_tickets = models.PositiveIntegerField(default=0, null=True, blank=True)  # VIP ticket limit, optional
    available_normal_tickets = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save method to handle available tickets logic."""
        if self.available_vip_tickets is None:
            self.available_vip_tickets = 0  # Set to 0 if no value is provided
        super().save(*args, **kwargs)



# Repository Pattern: Event Queries
class EventRepository:
    @staticmethod
    def get_upcoming_events():
        return Event.objects.filter(date__gte=datetime.date.today()).order_by('date')

    @staticmethod
    def get_events_by_category(category):
        return Event.objects.filter(category=category)


# Ticket Model (Updated)
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('canceled', 'Canceled'),
    ]
    TICKET_TYPE_CHOICES = [
        ('VIP', 'VIP'),
        ('Normal', 'Normal'),
    ]
    
    ticket_id = models.CharField(max_length=20, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_tickets', limit_choices_to={'role': 'customer'})
    purchase_date = models.DateTimeField(auto_now_add=True)
    ticket_type = models.CharField(max_length=50, choices=TICKET_TYPE_CHOICES, default='Normal')  # VIP or Normal
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.event.title} - {self.ticket_type}"



# Factory Pattern: Ticket Creation (Updated)
class TicketFactory:
    @staticmethod
    def create_ticket(event, buyer, ticket_type="Normal", price=None):
        # Check if the ticket type is valid
        if ticket_type not in ['VIP', 'Normal']:
            raise ValueError("Invalid ticket type. Must be either 'VIP' or 'Normal'.")
        
        # Validate VIP ticket availability
        if ticket_type == 'VIP' and event.available_vip_tickets <= 0:
            raise ValueError("No VIP tickets available for this event.")
        
        # If price is not provided, use default based on ticket type
        if ticket_type == 'VIP' and price is None:
            price = event.ticket_price * 2  # VIP ticket costs twice as much (example logic)
        elif ticket_type == 'Normal' and price is None:
            price = event.ticket_price  # Regular ticket price

        # Ensure that the event still has available tickets before creating a new one
        if ticket_type == 'VIP' and event.available_vip_tickets <= 0:
            raise ValueError("VIP tickets are sold out for this event.")
        elif ticket_type == 'Normal' and event.available_normal_tickets <= 0:
            raise ValueError("Normal tickets are sold out for this event.")
        
        # Proceed to create the ticket
        ticket = Ticket(
            event=event,
            buyer=buyer,
            ticket_type=ticket_type,
            price=price,
            status='active'
        )
        ticket.save()

        # Decrease the available tickets count (VIP or Normal)
        if ticket_type == 'VIP':
            event.available_vip_tickets -= 1
        elif ticket_type == 'Normal':
            event.available_normal_tickets -= 1
        
        event.save()  # Save event with updated ticket availability

        return ticket




# Observer Pattern: Notifications
class NotificationService:
    @staticmethod
    def send_ticket_confirmation(ticket):
        print(f"Ticket confirmation sent to {ticket.buyer.email}")

@receiver(post_save, sender=Ticket)
def notify_user(sender, instance, created, **kwargs):
    if created:
        NotificationService.send_ticket_confirmation(instance)



# Payment Model
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bkash', 'bKash'),
    ]
    payment_id = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, default='Completed')

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} ({self.method})"



# Strategy Pattern: Payment Processing
# Strategy Pattern: Payment Processing
class PaymentStrategy:
    def pay(self, amount):
        raise NotImplementedError("Subclasses must implement `pay` method.")

class CashPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Processing cash payment for ${amount}")

class bKashPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Processing bKash payment for ${amount}")

class PaymentContext:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def execute_payment(self, amount):
        self.strategy.pay(amount)

