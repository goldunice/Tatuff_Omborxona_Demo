from django.contrib import admin
from .models import Mahsulot, MahsulotBalans, MahsulotBalansTarix, KirdiChiqdi, KirdiChiqdiForm, OlchovBirligi


# === Mahsulot Admin ===
# Bu bo'lim mahsulotlarni admin panelida boshqarish uchun.
@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ('id', 'mahsulot_nomi')  # Admin panelda ko'rsatish uchun maydonlar
    list_display_links = ('id', 'mahsulot_nomi')  # Ushbu maydonlarga bosilsa, tegishli mahsulotga o'tadi
    search_fields = ('name',)  # Mahsulot nomi bo'yicha qidiruv imkoniyati
    ordering = ('id',)  # Mahsulotlarni id bo'yicha tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni


# === O'lchov birligi Admin ===
# Bu bo'lim o'lchov birliklarini boshqarish uchun.
@admin.register(OlchovBirligi)
class OlchovBirligiAdmin(admin.ModelAdmin):
    list_display = ('id', 'olchov_birligi')  # O'lchov birligini ko'rsatish
    list_display_links = ('id', 'olchov_birligi')  # ID va nomga bosilganda ko'rsatilgan o'lchovga o'tish
    search_fields = ('olchov_birligi',)  # O'lchov birligi bo'yicha qidiruv
    ordering = ('id',)  # O'lchov birligi ID bo'yicha tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni


# === MahsulotBalans Admin ===
# Bu bo'lim mahsulot balansi (ombordagi miqdor)ni boshqarish uchun.
@admin.register(MahsulotBalans)
class MahsulotBalansAdmin(admin.ModelAdmin):
    list_display = ('id', 'mahsulot_nomi', 'olchov_birligi', 'qoldiq')  # Ko'rinadigan ustunlar
    list_display_links = ('id', 'mahsulot_nomi')  # Mahsulotga bosilganda uning balansi ko'rsatiladi
    search_fields = ('mahsulot_nomi__mahsulot_nomi',)  # Mahsulot nomi bo'yicha qidiruv
    list_filter = ('mahsulot_nomi__mahsulot_nomi',)  # Mahsulot nomi bo'yicha filter
    ordering = ('id',)  # ID bo'yicha tartib
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni

    # Foydalanuvchining o'zi mahsulot uchun balance ni o'zgartira olmasligi zarur
    def has_add_permission(self, request):
        return False  # Mahsulot balansi qo'shish huquqi yo'q


# === MahsulotBalansTarix Admin ===
# Bu bo'lim mahsulot balansi tarixini boshqarish uchun.
@admin.register(MahsulotBalansTarix)
class MahsulotBalansTarixAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'mahsulot_nomi', 'miqdor', 'olchov_birligi__olchov_birligi', 'qoldiq', 'sana',
        'amaliyot_turi')  # Ko'rinadigan ustunlar
    search_fields = ('mahsulot_nomi__mahsulot_nomi', 'amaliyot_turi')  # Mahsulot nomi va turiga qidiruv
    list_filter = ('amaliyot_turi', 'sana')  # Operatsiya turi va sanasi bo'yicha filter
    date_hierarchy = 'sana'  # Sanalar bo'yicha navigatsiya
    ordering = ('-sana',)  # Teskari tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni

    # Foydalanuvchining o'zi tarix yarata olmasligi kerak
    def has_add_permission(self, request):
        return False  # Tarixga yangi yozuv qo'shish huquqi yo'q


# === KirdiChiqdi Admin ===
# Bu bo'lim kirim-chiqim operatsiyalarini boshqarish uchun.
@admin.register(KirdiChiqdi)
class KirdiChiqdiAdmin(admin.ModelAdmin):
    form = KirdiChiqdiForm  # Maxsus forma qo'llanadi
    list_display = (
    'id', 'mahsulot_nomi', 'miqdor', 'olchov_birligi__olchov_birligi', 'sana', 'amaliyot_turi')  # Ko'rinadigan ustunlar
    list_display_links = ('id', 'mahsulot_nomi')  # Mahsulotga bosilganda operatsiya ko'rsatiladi
    search_fields = ('mahsulot_nomi__mahsulot_nomi', 'amaliyot_turi')  # Mahsulot nomi va turiga qidiruv
    list_filter = ('amaliyot_turi', 'sana')  # Operatsiya turi va sanasi bo'yicha filter
    date_hierarchy = 'sana'  # Sanalar bo'yicha navigatsiya
    ordering = ('-sana',)  # Teskari tartibda tartib ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni


# Qo'shimcha konfiguratsiya
admin.site.site_header = "TATUFF Omborxona boshqaruv paneli"  # Panelning bosh sarlavhasi
admin.site.site_title = "Omborxona boshqaruvi administratori"  # Browser title
admin.site.index_title = "Omborxonani boshqarish uskunalar paneliga xush kelibsiz"  # Tashrif sarlavhasi
