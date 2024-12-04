from .models import Mahsulot, MahsulotBalans, MahsulotBalansTarix, KirdiChiqdi, KirdiChiqdiForm, OlchovBirligi
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateTimeRangeFilter
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.contrib import admin
from django.http import HttpResponse
import xlsxwriter

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.html import format_html

from django_otp.admin import OTPAdminSite

admin.site.__class__ = OTPAdminSite





class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (  # Add the new field to admin
        ('Additional Info', {'fields': ('profile_image',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('profile_image',)}),
    )
    # Customizing list display to include image preview
    list_display = ['id', 'username', 'email','first_name','last_name','is_staff','is_active', 'profile_image_preview']

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.profile_image.url)
        return "No Image"

    profile_image_preview.short_description = 'Profile Image'


admin.site.register(CustomUser, CustomUserAdmin)


def download_pdf(self, request, queryset):
    model_name = self.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle('PDF Report')

    ordered_queryset = queryset.order_by('-id')

    headers = ["T/r"] + [field.verbose_name for field in self.model._meta.fields]
    data = [headers]
    for index, obj in enumerate(ordered_queryset, 1):
        data_row = [index]
        data_row += [(getattr(obj, field.name)) for field in self.model._meta.fields]
        data.append(data_row)

    table = Table(data)
    table.setStyle(TableStyle(
        [
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]
    ))

    canvas_width = 550
    canvas_height = 550

    table.wrapOn(pdf, canvas_width, canvas_height)
    table.drawOn(pdf, 20, canvas_height - len(data))

    pdf.save()

    return response


download_pdf.short_description = 'Tanlangan maydonlarni PDF fayl sifatda yuklash'


def download_excel(modeladmin, request, queryset):
    model_name = modeladmin.model.__name__
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={model_name}.xlsx'
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    headers = ["T/r"] + [field.verbose_name for field in modeladmin.model._meta.fields]

    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    for row_num, obj in enumerate(queryset, 1):
        worksheet.write(row_num, 0, row_num)
        for col_num, field in enumerate(modeladmin.model._meta.fields, 1):
            value = str(getattr(obj, field.name))
            worksheet.write(row_num, col_num, value)

    workbook.close()
    return response


download_excel.short_description = "Tanlangan maydonlarni Excel fayl sifatida yuklab olish"


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
            return queryset.filter(mahsulot_nomi__olchov_birligi__id=self.value())
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
    actions = [download_excel,
               download_pdf]  # Mahsulotning joriy balansi haqida malumot olish uchun fayl sifatida yuklab olish xizmati

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
    list_filter = [
        ('sana', DateTimeRangeFilter)]  # Operatsiya turi va sanasi bo'yicha filter ('amaliyot_turi', 'sana'),
    date_hierarchy = 'sana'  # Sanalar bo'yicha navigatsiya
    ordering = ('-id',)  # Teskari tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni
    actions = [download_excel, download_pdf]  # Tarixni Excel fayl qilib yuklab olish xizmati

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
# admin.site.site_header = "Tatuff Omborxona Boshqaruv Paneliga Xush Kelibsiz"  # Panelning bosh sarlavhasi
# admin.site.site_title = "Omborxona boshqaruvi administratori"  # Browser title
admin.site.index_title = "TATUFF Ombor"  # Tashrif sarlavhasi
