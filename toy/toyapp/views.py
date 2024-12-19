from django.shortcuts import render, get_object_or_404, redirect
from .models import Toy, Category, Review, Favorite
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserRegisterForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test

def toy_list(request):
    category = request.GET.get('category')
    toys = Toy.objects.all()

    if category:
        toys = toys.filter(category__name__icontains=category)  # กรองตามหมวดหมู่

    categories = Category.objects.all()
    return render(request, 'toy_list.html', {'toys': toys, 'categories': categories})




def toy_detail(request, toy_id):
    toy = get_object_or_404(Toy, id=toy_id)
    reviews = toy.reviews.all()
    average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.toy = toy
            review.save()
            return redirect('toy_detail', toy_id=toy.id)

    return render(request, 'toy_detail.html', {
        'toy': toy, 'reviews': reviews, 'average_rating': average_rating, 'form': form
    })


def add_to_favorites(request, toy_id):
    toy = get_object_or_404(Toy, id=toy_id)
    Favorite.objects.get_or_create(user=request.user, toy=toy)
    return redirect('toy_detail', toy_id=toy.id)


def favorites_list(request):
    favorites = request.user.favorites.all()
    return render(request, 'favorites_list.html', {'favorites': favorites})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@csrf_exempt
def user_login(request):
    if request.user.is_authenticated:
        # ส่งผู้ใช้ที่เข้าสู่ระบบแล้วไปหน้าที่เหมาะสม
        if request.user.is_superuser:
            return redirect('admin_home')
        return redirect('toy_list')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('admin_home')
            return redirect('toy_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')



# ฟังก์ชันตรวจสอบว่าเป็นแอดมิน
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def add_toy(request):
    if request.method == 'POST':
        # ดึงข้อมูลจาก request.POST และ request.FILES
        name = request.POST.get('name')
        price = request.POST.get('price')
        age_range = request.POST.get('age_range')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        # ตรวจสอบว่า Category มีอยู่หรือไม่
        category = Category.objects.get(id=category_id)

        # บันทึกข้อมูลของเล่นใหม่
        Toy.objects.create(
            name=name,
            price=price,
            age_range=age_range,
            description=description,
            image=image,
            category=category
        )
        return redirect('toy_list')  # หลังบันทึกเสร็จให้กลับไปที่หน้าแสดงของเล่น

    # ส่งข้อมูลหมวดหมู่ไปยัง Template
    categories = Category.objects.all()
    return render(request, 'admin/add_toy.html', {'categories': categories})

@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('admin_home')  # กลับไปหน้าแอดมินหลังเพิ่มหมวดหมู่
    return render(request, 'admin/add_category.html')


