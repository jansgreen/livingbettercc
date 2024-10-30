from django.urls import path
from .views import group_list, group_create, \
    group_update, user_list, add_and_remove_group_to_user, add_and_remove_permission_to_groups,\
    InviteFriendView, accept_invite, invite_success

urlpatterns = [
    path('user_list/', user_list, name='user_list'),
    path('add_and_remove_group_to_user/<int:user_id>/', add_and_remove_group_to_user, name='add_and_remove_group_to_user'),
    path('add_and_remove_permission_to_groups/<int:group_id>/', add_and_remove_permission_to_groups, name='add_and_remove_permission_to_groups'),

    path('', group_list, name='group_list'),
    path('groups/create/', group_create, name='group_create'),
    path('groups/<int:pk>/update/', group_update, name='group_update'),

    path('invite/', InviteFriendView.as_view(), name='invite_friend'),
    path('accept-invite/<uidb64>/<token>/<int:group_id>/', accept_invite, name='accept_invite'),
    path('invite_success/', invite_success, name='invite_success'), 

]
