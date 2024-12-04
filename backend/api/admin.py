from django.contrib import admin
from .models import User, Event, Ticket, Payment, TicketConfig

# Register your models
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'date', 'time', 'category', 'ticket_price', 'available_tickets')
    list_filter = ('category', 'date')
    search_fields = ('title', 'location')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'event', 'buyer', 'purchase_date', 'status')
    list_filter = ('status', 'event')
    search_fields = ('ticket_id', 'buyer__username')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'amount', 'method', 'status', 'payment_date')
    list_filter = ('method', 'status')
    search_fields = ('payment_id',)


@admin.register(TicketConfig)
class TicketConfigAdmin(admin.ModelAdmin):
    list_display = ('max_tickets_per_user', 'default_ticket_price')
