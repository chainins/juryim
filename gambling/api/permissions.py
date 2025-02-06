from rest_framework import permissions

class IsGameActive(permissions.BasePermission):
    """
    Custom permission to only allow betting on active games.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed if the game is active
        return obj.status == 'active'

class IsBetOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a bet to view it.
    """
    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the bet
        return obj.user == request.user

class CanPlaceBet(permissions.BasePermission):
    """
    Custom permission to check if user can place a bet.
    """
    def has_permission(self, request, view):
        # Check if user has sufficient balance
        if not hasattr(request.user, 'financial_account'):
            return False
            
        # Additional checks can be added here
        # (e.g., user verification status, betting limits, etc.)
        return True 