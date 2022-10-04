from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Post
from .filters import PostFilter
from .forms import PostCreateForm
from . import resources


class PostsList(LoginRequiredMixin, ListView):
    model = Post
    ordering = 'created'
    template_name = 'news_all.html'
    context_object_name = 'posts'
    # Paginating
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class PostsListSearch(PermissionRequiredMixin, ListView):
    permission_required = ('news.view_post',)
    model = Post
    ordering = 'created'
    template_name = 'news_all_search.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'post'
    # Определяет, как будем называть первичный ключ при определении url
    pk_url_kwarg = 'id'


def get_post_type(request_path):
    """
    Возвращает тип статьи, в зависимости от адреса запроса
    """
    post_type = resources.post_type_news
    if 'article' in request_path:
        post_type = resources.post_type_article
    return {'short': post_type, 'name': resources.get_post_type_name(post_type)}


class PostCreate(CreateView):
    """ Создание поста (новости или статьи) """
    form_class = PostCreateForm
    model = Post
    template_name = 'post_create.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст заголовок
        """
        context = super().get_context_data(**kwargs)
        context['header_text'] = f'Create {get_post_type(self.request.path)["name"]}'
        context['post_type_valid'] = True
        return context

    def form_valid(self, form):
        """
        Заполняет тип у созданной статьи
        """
        post = form.save(commit=False)
        post.type = get_post_type(self.request.path)['short']
        return super().form_valid(form)


class PostEdit(LoginRequiredMixin, UpdateView):
    """ Редактирование новости или статьи """
    form_class = PostCreateForm
    model = Post
    template_name = 'post_create.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст:
            1. Заголовок
            2. Соответствует ли тип статьи по коду типу статьи в запросе
            3. Тип статьи
            4. Код статьи
        """
        post_type = get_post_type(self.request.path)

        context = super().get_context_data(**kwargs)
        context['header_text'] = f'Edit {post_type["name"]}'
        context['post_type_valid'] = post_type['short'] == self.object.type
        context['post_type'] = f'{post_type["name"]}'
        context['post_pk'] = f'{self.object.id}'
        return context


class PostDelete(DeleteView):
    """ Удаление новости или статьи """
    model = Post
    template_name = 'post_delete.html'
    # перенаправление после удаления товара
    success_url = reverse_lazy('post_list')

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст:
            1. Заголовок
            2. Соответствует ли тип статьи по коду типу статьи в запросе
            3. Тип статьи
            4. Код статьи
        """
        post_type = get_post_type(self.request.path)

        context = super().get_context_data(**kwargs)
        context['header_text'] = f'Delete {post_type["name"]}'
        context['post_type_valid'] = post_type['short'] == self.object.type
        context['post_type'] = f'{post_type["name"]}'
        context['post_pk'] = f'{self.object.id}'
        return context
