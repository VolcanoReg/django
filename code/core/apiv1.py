from ninja import NinjaAPI, Schema
from django.contrib.auth.models import User
from pydantic import validator
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
import re

# Inisialisasi Django Ninja API
apiv1 = NinjaAPI()

# Mendaftarkan router untuk login dan refresh token
apiv1.add_router("/auth/", mobile_auth_router)

# Menginisialisasi JWT Auth Guard
apiAuth = HttpJwtAuth()

# ----------------------------------------------------
# 1. Endpoint Basic GET & POST
# ----------------------------------------------------

@apiv1.get('hello/')
def helloApi(request):
    return "Menyala abangkuh ..."

@apiv1.post('hello/')
def helloPost(request):
    if 'nama' in request.POST:
        return f"Selamat menikmati ya {request.POST['nama']}"
    return "Selamat tinggal dan pergi lagi"

# ----------------------------------------------------
# 2. Endpoint Kalkulator (GET & POST)
# ----------------------------------------------------

@apiv1.get('calc/{nil1}/{opr}/{nil2}')
def calculator(request, nil1: int, opr: str, nil2: int):
    hasil = nil1 + nil2
    if opr == '-':
        hasil = nil1 - nil2
    elif opr == 'x':
        hasil = nil1 * nil2
    return {'nilai1': nil1, 'nilai2': nil2, 'operator': opr, 'hasil': hasil}

# Skema untuk Validasi POST Kalkulator
class Kalkulator(Schema):
    nil1: int
    nil2: int
    opr: str
    hasil: int = 0

    def calcHasil(self):
        hasil = self.nil1 + self.nil2
        if self.opr == '-':
            hasil = self.nil1 - self.nil2
        elif self.opr == 'x':
            hasil = self.nil1 * self.nil2
        return hasil

@apiv1.post('calc')
def postCalc(request, skim: Kalkulator):
    skim.hasil = skim.calcHasil()
    return skim

# ----------------------------------------------------
# 3. Endpoint Mock PUT & DELETE Users
# ----------------------------------------------------

@apiv1.put('users/{id}')
def userupdate(request, id: int):
    # Mengambil nilai 'nama' dari body request jika ada
    nama_baru = request.POST.get('nama', 'User Baru')
    return f"User dengan id {id} Nama aslinya adalah Herdiono kemudian diganti menjadi {nama_baru}"

@apiv1.delete('users/{id}')
def userDelete(request, id: int):
    return f"Hapus user dengan id: {id}"

# ----------------------------------------------------
# 4. Skema Validasi dan Endpoint Registrasi User
# ----------------------------------------------------

# Skema Input
class Register(Schema):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str

    @validator("username")
    def validate_username(cls, value):
        if len(value) < 5:
            raise ValueError("Username harus lebih dari 4 karakter")
        return value

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password harus lebih dari 8 karakter")
        pattern = r'^(?=.*[A-Za-z])(?=.*\d).+$'
        if not re.match(pattern, value):
            raise ValueError("Password harus mengandung huruf dan angka")
        return value

# Skema Output (Response)
class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

@apiv1.post('register/', response=UserOut)
def register(request, data: Register):
    """
    Endpoint untuk registrasi pengguna dengan validasi inputan:
    - username: minimal terdiri dari 5 karakter
    - password: minimal terdiri dari 8 karakter dan harus mengandung huruf dan angka
    """
    newUser = User.objects.create_user(
        username=data.username,
        password=data.password,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name
    )
    return newUser

# ----------------------------------------------------
# 5. Endpoint Terproteksi JWT (Login Required)
# ----------------------------------------------------

@apiv1.get('mycourses/', auth=apiAuth)
def getMyCourses(request):
    user = User.objects.get(pk=request.user.id)
    return {"message": f"Halo {user.username}, ini adalah daftar course Anda."}

@apiv1.post('course/{id}/enroll/', auth=apiAuth)
def courseEnrollment(request, id: int):
    user = User.objects.get(pk=request.user.id)
    return {"message": f"User {user.username} berhasil mendaftar di course dengan ID {id}"}

@apiv1.post('comments/', auth=apiAuth)
def postComment(request, comment_text: str):
    user = User.objects.get(pk=request.user.id)
    return {"status": "berhasil", "user": user.username, "komentar": comment_text}
