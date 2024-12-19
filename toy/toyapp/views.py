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
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

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
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # ตรวจสอบว่ารหัสผ่านตรงกัน
        if password != password2:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
            return redirect('register')

        # ตรวจสอบว่าชื่อผู้ใช้ซ้ำหรือไม่
        if User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้มีอยู่แล้ว")
            return redirect('register')

        # ตรวจสอบว่าอีเมลซ้ำหรือไม่
        if User.objects.filter(email=email).exists():
            messages.error(request, "อีเมลนี้มีอยู่แล้ว")
            return redirect('register')

        # สร้างผู้ใช้ใหม่
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ")
        return redirect('login')

    return render(request, 'register.html')

def user_login(request):
    if request.user.is_authenticated:
        # หากผู้ใช้เข้าสู่ระบบแล้ว
        if request.user.is_superuser:
            return redirect('admin_home')
        return redirect('toy_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # ตรวจสอบข้อมูลผู้ใช้
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "เข้าสู่ระบบสำเร็จ")
            if user.is_superuser:
                return redirect('admin_home')
            return redirect('toy_list')
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    return render(request, 'login.html')


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


