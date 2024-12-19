from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Toy(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    age_range = models.CharField(max_length=50)  # เช่น 3-5 ปี
    description = models.TextField()
    image = models.ImageField(upload_to='toys/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='toys')

    def __str__(self):
        return self.name

class Review(models.Model):
    toy = models.ForeignKey(Toy, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5 คะแนน
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.toy.name} ({self.rating})"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    toy = models.ForeignKey(Toy, on_delete=models.CASCADE, related_name='favorited_by')

    def __str__(self):
        return f"{self.user.username} - {self.toy.name}"
