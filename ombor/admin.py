from .models import Mahsulot, MahsulotBalans, MahsulotBalansTarix, KirdiChiqdi, KirdiChiqdiForm, OlchovBirligi
from django.utils.translation import gettext_lazy as _
from django.contrib import admin


# === O'lchov birligi Admin ===
# Bu bo'lim o'lchov birliklarini boshqarish uchun.
@admin.register(OlchovBirligi)
class OlchovBirligiAdmin(admin.ModelAdmin):
    list_display = ('id', 'olchov_birligi')  # O'lchov birligini ko'rsatish
    list_display_links = ('id', 'olchov_birligi')  # ID va nomga bosilganda ko'rsatilgan o'lchovga o'tish
    search_fields = ('olchov_birligi',)  # O'lchov birligi bo'yicha qidiruv
    ordering = ('-id',)  # O'lchov birligi ID bo'yicha tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni

    def has_change_permission(self, request, obj=None):
        return False


# === Custom Filter ===
class OlchovBirligiFilter(admin.SimpleListFilter):
    title = _('O‘lchov birligi')  # Admin paneldagi filter nomi
    parameter_name = 'olchov_birligi'

    def lookups(self, request, model_admin):
        """
        Filterda faqat `KirdiChiqdi` modelida mavjud o'lchov birliklari ko'rinadi.
        """
        # KirdiChiqdi modelida ishlatilgan o'lchov birliklarini oling
        olchov_birliklar = (
            KirdiChiqdi.objects.values_list('mahsulot_nomi__olchov_birligi__id',
                                            'mahsulot_nomi__olchov_birligi__olchov_birligi')
            .distinct()
        )
        return [(ob[0], ob[1]) for ob in olchov_birliklar]

    def queryset(self, request, queryset):
        """
        Foydalanuvchi filterni tanlaganda, mos yozuvlarni qaytaradi.
        """
        if self.value():
            return queryset.filter(olchov_birligi__id=self.value())
        return queryset


# === Mahsulot Admin ===
# Bu bo'lim mahsulotlarni admin panelida boshqarish uchun.
@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ('id', 'mahsulot_nomi', 'olchov_birligi')  # Admin panelda ko'rsatish uchun maydonlar
    list_display_links = ('id', 'mahsulot_nomi')  # Ushbu maydonlarga bosilsa, tegishli mahsulotga o'tadi
    search_fields = ('mahsulot_nomi',)  # Mahsulot nomi bo'yicha qidiruv imkoniyati
    ordering = ('-id',)  # Mahsulotlarni id bo'yicha tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni

    def has_change_permission(self, request, obj=None):
        return False


# === MahsulotBalans Admin ===
# Bu bo'lim mahsulot balansi (ombordagi miqdor)ni boshqarish uchun.
@admin.register(MahsulotBalans)
class MahsulotBalansAdmin(admin.ModelAdmin):
    list_display = ('id', 'mahsulot_nomi', 'mahsulot_nomi__olchov_birligi', 'qoldiq')  # Ko'rinadigan ustunlar
    list_display_links = ('id', 'mahsulot_nomi')  # Mahsulotga bosilganda uning balansi ko'rsatiladi
    search_fields = ('mahsulot_nomi__mahsulot_nomi',)  # Mahsulot nomi bo'yicha qidiruv
    list_filter = (OlchovBirligiFilter,)  # Custom filterni qo'shish
    ordering = ('-id',)  # ID bo'yicha tartib
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mahsulot_nomi__olchov_birligi":
            # Faqat `KirdiChiqdi` orqali kiritilgan `OlchovBirligi`larni ko'rsatish
            kwargs["queryset"] = OlchovBirligi.objects.filter(
                id__in=KirdiChiqdi.objects.values('mahsulot_nomi__olchov_birligi'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Foydalanuvchining o'zi mahsulot uchun balance ni o'zgartira olmasligi zarur
    def has_add_permission(self, request):
        return False  # Mahsulot balansi qo'shish huquqi yo'q

    # Foydalanuvchining mahsulot uchun balansi o'zgartirish huquqini cheklash
    def has_change_permission(self, request, obj=None):
        return False  # Mahsulot balansi o'zgartirish huquqi yo'q

    # O'chirish ruxsatini o'chirib qo'ying
    def has_delete_permission(self, request, obj=None):
        return False
    # Ob'ektlarni o'chirishni oldini olish


# === MahsulotBalansTarix Admin ===
# Bu bo'lim mahsulot balansi tarixini boshqarish uchun.
@admin.register(MahsulotBalansTarix)
class MahsulotBalansTarixAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'mahsulot_nomi', 'miqdor', 'mahsulot_nomi__olchov_birligi', 'qoldiq', 'sana',
        'amaliyot_turi')  # Ko'rinadigan ustunlar
    search_fields = ('mahsulot_nomi__mahsulot_nomi', 'amaliyot_turi')  # Mahsulot nomi va turiga qidiruv
    list_filter = ('amaliyot_turi', 'sana')  # Operatsiya turi va sanasi bo'yicha filter
    # readonly_fields = ('olchov_birligi',)  # Faqat o'qish uchun maydon
    date_hierarchy = 'sana'  # Sanalar bo'yicha navigatsiya
    ordering = ('-id',)  # Teskari tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni

    # Foydalanuvchining o'zi tarix yarata olmasligi kerak
    def has_add_permission(self, request):
        return False  # Tarixga yangi yozuv qo'shish huquqi yo'q

    # Foydalanuvchining kirdi Chiqdi tarixi uchun o'zgartirish huquqini cheklash
    def has_change_permission(self, request, obj=None):
        return False  # Kirdi Chiqdi o'zgartirish huquqi yo'q

    # O'chirish ruxsatini o'chirib qo'ying
    def has_delete_permission(self, request, obj=None):
        return False
    # Ob'ektlarni o'chirishni oldini olish


# === KirdiChiqdi Admin ===
# Bu bo'lim kirim-chiqim operatsiyalarini boshqarish uchun.
@admin.register(KirdiChiqdi)
class KirdiChiqdiAdmin(admin.ModelAdmin):
    form = KirdiChiqdiForm  # Maxsus forma qo'llanadi
    list_display = (
        'id', 'mahsulot_nomi', 'miqdor', 'mahsulot_nomi__olchov_birligi', 'sana',
        'amaliyot_turi')  # Ko'rinadigan ustunlar
    list_display_links = ('id', 'mahsulot_nomi')  # Mahsulotga bosilganda operatsiya ko'rsatiladi
    search_fields = ('mahsulot_nomi__mahsulot_nomi', 'amaliyot_turi')  # Mahsulot nomi va turiga qidiruv
    list_filter = ('amaliyot_turi', 'sana')  # Operatsiya turi va sanasi bo'yicha filter
    date_hierarchy = 'sana'  # Sanalar bo'yicha navigatsiya
    ordering = ('-sana',)  # Teskari tartibda tartib ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni

    def has_change_permission(self, request, obj=None):
        return False


# Qo'shimcha konfiguratsiya
admin.site.site_header = "Tatuff Omborxona Boshqaruv Paneliga Xush Kelibsiz"  # Panelning bosh sarlavhasi
admin.site.site_title = "Omborxona boshqaruvi administratori"  # Browser title
admin.site.index_title = "Omborxonani boshqarish uskunalar paneliga xush kelibsiz"  # Tashrif sarlavhasi
