from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.pagination import LimitOffsetPagination

from api.permissions import AuthorOrReadOnly, ReadOnly
from api.serializers import (CommentSerializer,
                             GroupSerializer,
                             PostSerializer,
                             FollowSerializer)
from posts.models import Post, Group


class PostViewSet(viewsets.ModelViewSet):
    """Представление для управления постами."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        """Сохраняет новый пост."""
        serializer.save(author=self.request.user)

    def get_permissions(self):
        """Возвращает разрешения для текущего действия.s"""
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для просмотра групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Представление для управления комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_permissions(self):
        """Возвращает разрешения для текущего действия."""
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_post(self):
        """Возвращает связанный пост для запроса."""
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return post

    def perform_create(self, serializer):
        """Создает новый комментарий."""
        serializer.save(author=self.request.user, post=self.get_post())

    def get_queryset(self):
        """Фильтрует комментарии по связанному посту."""
        post = self.get_post()
        queryset = post.comments.all()
        return queryset


class CreateListViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Базовое представление для создания и просмотра списков объектов."""

    pass


class FollowViewSet(CreateListViewSet):
    """Представление для управления подписками."""

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Возвращает список подписчиков пользователя, совершающего запрос."""
        return self.request.user.followers.all()

    def perform_create(self, serializer):
        """
        Сохраняет новую подписку с текущим пользователем
        в качестве подписчика.
        """
        serializer.save(user=self.request.user,)
