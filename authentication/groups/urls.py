from django.urls import path
from .views import group_list, group_create, \
    group_update, group_delete, user_list, add_and_remove_group_to_user, add_and_remove_permission_to_groups, update_user_type, bulk_update_user_type, delete_user,\
    InviteFriendView, accept_invite, invite_success, complete_scholarship_info


urlpatterns = [
    path('user_list/', user_list, name='user_list'),
    path('update_user_type/<int:user_id>/', update_user_type, name='update_user_type'),
    path('bulk_update_user_type/', bulk_update_user_type, name='bulk_update_user_type'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
    path('add_and_remove_group_to_user/<int:user_id>/', add_and_remove_group_to_user, name='add_and_remove_group_to_user'),
    path('add_and_remove_permission_to_groups/<int:group_id>/', add_and_remove_permission_to_groups, name='add_and_remove_permission_to_groups'),

    path('', group_list, name='group_list'),
    path('groups/create/', group_create, name='group_create'),
    path('groups/<int:pk>/update/', group_update, name='group_update'),
    path('groups/<int:pk>/delete/', group_delete, name='group_delete'),

    path('invite/', InviteFriendView.as_view(), name='invite_friend'), 
    path('accept-invite/<uuid:token>/', accept_invite, name='accept_invite'),
    path('scholarship-info/', complete_scholarship_info, name='complete_scholarship_info'),
    path('invite_success/', invite_success, name='invite_success'), 

]
