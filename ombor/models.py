from django.core.exceptions import ValidationError
from django.db import models
from django import forms
import re


# === O'lchov birligi Modeli ===
# Bu model miqdor turini saqlash uchun ishlatiladi.
class OlchovBirligi(models.Model):
    olchov_birligi = models.CharField(max_length=255, unique=True)  # Miqdor turi

    class Meta:
        verbose_name = "O'lchov Birlig"
        verbose_name_plural = "O'lchov Birliglar"

    def clean(self):

        # O'lchov birligi faqat harflardan iboratligini tekshirish
        if not re.fullmatch(r'^[a-zA-Zа-яА-ЯёЁ]+$', self.olchov_birligi):
            raise ValidationError(
                "O'lchov birligi faqat harflardan iborat bo'lishi kerak! Maxsus belgilar yoki raqamlar kiritish mumkin emas.")

        # O'lchov birligini tekshirish: mavjudligini aniqlash
        if OlchovBirligi.objects.filter(olchov_birligi__iexact=self.olchov_birligi).exclude(pk=self.pk).exists():
            raise ValidationError(f"'{self.olchov_birligi}' nomli o'lchov birligi bazada allaqachon mavjud!")

    def save(self, *args, **kwargs):
        # Ma'lumotni formatlash: birinchi harf katta, qolganlari kichik
        if self.olchov_birligi:
            self.olchov_birligi = self.olchov_birligi.capitalize()
        # Avval clean() chaqiriladi, keyin saqlash amalga oshiriladi
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.olchov_birligi  # Admin panelda miqdor turi ko'rsatadi


# === Mahsulot Modeli ===
# Bu model mahsulot nomini saqlash uchun ishlatiladi.
class Mahsulot(models.Model):
    mahsulot_nomi = models.CharField(max_length=255, unique=True)  # Mahsulot nomi

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def clean(self):
        # Mahsulot nomi faqat harflardan iboratligini tekshirish
        if not re.fullmatch(r'^[a-zA-Zа-яА-ЯёЁ]+$', self.mahsulot_nomi):
            raise ValidationError(
                "Mahsulot nomi faqat harflardan iborat bo'lishi kerak! Maxsus belgilar yoki raqamlar kiritish mumkin emas.")

        # Mahsulot nomining unikal ekanligini tekshirish
        if Mahsulot.objects.filter(mahsulot_nomi__iexact=self.mahsulot_nomi).exclude(pk=self.pk).exists():
            raise ValidationError(f"'{self.mahsulot_nomi}' nomli mahsulot bazada allaqachon mavjud!")

    def save(self, *args, **kwargs):
        # Mahsulot nomini formatlash: birinchi harf katta, qolganlari kichik
        if self.mahsulot_nomi:
            self.mahsulot_nomi = self.mahsulot_nomi.capitalize()
        # Avval clean() chaqiriladi, keyin saqlash amalga oshiriladi
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.mahsulot_nomi  # Admin panelda mahsulot nomini ko'rsatadi


# === Mahsulot Balans Modeli ===
# Bu model mahsulotning ombordagi qolgan miqdorini saqlash uchun ishlatiladi.
class MahsulotBalans(models.Model):
    mahsulot_nomi = models.ForeignKey(Mahsulot, on_delete=models.SET_NULL, null=True)  # Mahsulotga bog'langan
    qoldiq = models.PositiveIntegerField(default=0)  # Ombordagi qolgan mahsulot miqdori
    olchov_birligi = models.ForeignKey(OlchovBirligi, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Mahsulot Joriy Balansi"
        verbose_name_plural = "Mahsulot Joriy Balansi"

    def __str__(self):
        return f"{self.mahsulot_nomi} {self.qoldiq} {self.olchov_birligi}"  # Admin panelda mahsulot va miqdorini ko'rsatadi


# === Mahsulot Balans Tarix Modeli ===
# Bu model mahsulot balansi tarixini saqlash uchun ishlatiladi.
class MahsulotBalansTarix(models.Model):
    mahsulot_nomi = models.ForeignKey(Mahsulot, on_delete=models.SET_NULL, null=True)  # Mahsulotga bog'langan
    miqdor = models.PositiveIntegerField()  # Mahsulot miqdori
    olchov_birligi = models.ForeignKey(OlchovBirligi, on_delete=models.SET_NULL, null=True)  # O'lchov birligi
    qoldiq = models.PositiveIntegerField()  # Qolgan mahsulot miqdori
    sana = models.DateTimeField()  # O'zgarish sanasi
    amaliyot_turi = models.CharField(max_length=5)  # Operatsiya turi ("Kirdi" yoki "Chiqdi")

    class Meta:
        verbose_name = "Mahsulot Balans Tarixi"
        verbose_name_plural = "Mahsulot Balans Tarixi"

    def save(self, *args, **kwargs):
        # Asl save metodini chaqirish
        super().save(*args, **kwargs)

        # MahsulotBalans modelini yangilash
        if self.mahsulot_nomi:
            # Mahsulot uchun MahsulotBalans ma'lumotini olish yoki yaratish
            mahsulot_balans, yaratilgan = MahsulotBalans.objects.get_or_create(
                mahsulot_nomi=self.mahsulot_nomi,
                defaults={'qoldiq': self.qoldiq}
            )
            # Oxirgi qolgan miqdorni yangilash
            mahsulot_balans.qoldiq = self.qoldiq
            mahsulot_balans.save()

    def __str__(self):
        return f"{self.mahsulot_nomi} {self.miqdor} {self.olchov_birligi} {self.qoldiq}  {self.sana} {self.amaliyot_turi}"


# === Kirdi Chiqdi Modeli ===
# Bu model mahsulotlarning kirim va chiqim operatsiyalarini boshqarish uchun ishlatiladi.
class KirdiChiqdi(models.Model):
    # Kirim va chiqim turini belgilash
    Kirdi_Chiqdi = (
        ("Kirdi", "Kirdi"),  # Kirim
        ("Chiqdi", "Chiqdi")  # Chiqim
    )
    mahsulot_nomi = models.ForeignKey(Mahsulot, on_delete=models.SET_NULL, null=True)  # Mahsulotga bog'langan
    miqdor = models.PositiveIntegerField(default=0)  # Mahsulot miqdori
    olchov_birligi = models.ForeignKey(OlchovBirligi, on_delete=models.SET_NULL, null=True)  # O'lchov birligi
    sana = models.DateTimeField(auto_now_add=True)  # Operatsiya sanasi
    amaliyot_turi = models.CharField(max_length=15, choices=Kirdi_Chiqdi)  # Operatsiya turi ("Kirdi" yoki "Chiqdi")

    class Meta:
        verbose_name = "Kirdi Chiqdi"
        verbose_name_plural = "Kirdi Chiqdi"

    def save(self, *args, **kwargs):
        # Asl save metodini chaqirish
        super().save(*args, **kwargs)

        # MahsulotBalansTarix uchun yozuv qo'shish yoki yangilash
        if self.mahsulot_nomi:
            mahsulot_tarix = MahsulotBalansTarix.objects.filter(mahsulot_nomi=self.mahsulot_nomi,
                                                                olchov_birligi=self.olchov_birligi).last()

            if mahsulot_tarix is None:
                # Mahsulot uchun tarix mavjud bo'lmasa, yangi yozuv yaratish
                MahsulotBalansTarix.objects.create(
                    mahsulot_nomi=self.mahsulot_nomi,
                    miqdor=self.miqdor,
                    olchov_birligi=self.olchov_birligi,
                    qoldiq=self.miqdor,
                    sana=self.sana,
                    amaliyot_turi="Kirdi" if self.amaliyot_turi == "Kirdi" else "Chiqdi"
                )
            else:
                # Ombor balansini yangilash
                if self.amaliyot_turi == "Kirdi":
                    yangi_qoldiq = mahsulot_tarix.qoldiq + self.miqdor
                elif self.amaliyot_turi == "Chiqdi":
                    yangi_qoldiq = mahsulot_tarix.qoldiq - self.miqdor
                    if yangi_qoldiq < 0:  # Omborda mahsulot yetarli emas
                        raise ValidationError("Omborda mahsulot yetarli emas.")

                # Yangi tarix yozuvini qo'shish
                MahsulotBalansTarix.objects.create(
                    mahsulot_nomi=self.mahsulot_nomi,
                    miqdor=self.miqdor,
                    olchov_birligi=self.olchov_birligi,
                    qoldiq=yangi_qoldiq,
                    sana=self.sana,
                    amaliyot_turi="Kirdi" if self.amaliyot_turi == "Kirdi" else "Chiqdi"
                )

    def __str__(self):
        return f"{self.mahsulot_nomi} {self.miqdor} {self.olchov_birligi} {self.sana} {self.amaliyot_turi}"






# === Kirdi Chiqdi Form ===
class KirdiChiqdiForm(forms.ModelForm):
    class Meta:
        model = KirdiChiqdi
        fields = "__all__"  # Barcha maydonlarni formaga qo'shish

    def clean(self):
        cleaned_data = super().clean()
        mahsulot_nomi = cleaned_data.get("mahsulot_nomi")
        miqdor = cleaned_data.get("miqdor")
        olchov_birligi = cleaned_data.get("olchov_birligi")
        amaliyot_turi = cleaned_data.get("amaliyot_turi")

        # 1. Har bir maydonning qiymati kiritilganligini tekshirish
        if not mahsulot_nomi:
            raise ValidationError({"mahsulot_nomi": "Mahsulot nomi kiritilishi shart!"})
        if not olchov_birligi:
            raise ValidationError({"olchov_birligi": "O'lchov birligi kiritilishi shart!"})
        if miqdor is None or miqdor <= 0:
            raise ValidationError({"miqdor": "Mahsulot miqdori nol yoki manfiy bo'lishi mumkin emas!"})

        # 2. Ombordagi mahsulot balansini tekshirish
        if amaliyot_turi == "Chiqdi":
            mahsulot_balans = MahsulotBalans.objects.filter(mahsulot_nomi=mahsulot_nomi).first()
            if not mahsulot_balans:
                raise ValidationError({"mahsulot_nomi": "Bu mahsulot omborda mavjud emas!"})
            if miqdor > mahsulot_balans.qoldiq:
                raise ValidationError({"miqdor": "Omborda yetarli mahsulot mavjud emas!"})

        # 3. Kirim va chiqimdagi o'lchov birligini tekshirish
        if amaliyot_turi == "Chiqdi":
            oxirgi_kiruv = MahsulotBalansTarix.objects.filter(
                mahsulot_nomi=mahsulot_nomi, amaliyot_turi="Kirdi"
            ).last()
            if oxirgi_kiruv and oxirgi_kiruv.olchov_birligi != olchov_birligi:
                raise ValidationError({"olchov_birligi": "Kiritilgan o'lchov birligi so'nggi kirimdagi o'lchov birligiga mos emas!"})

        return cleaned_data



























#
# # === Kirdi Chiqdi Formani tekshirisih ===
# # Bu forma admin panelda foydalanuvchidan ma'lumotlarni to'g'ri kiritishni talab qiladi.
# class KirdiChiqdiForm(forms.ModelForm):
#     class Meta:
#         model = KirdiChiqdi
#         fields = "__all__"  # Barcha maydonlarni formaga qo'shish
#
#     def clean(self):
#         # Foydalanuvchi tomonidan kiritilgan ma'lumotlarni olish
#         cleaned_data = super().clean()
#         mahsulot_nomi = cleaned_data.get("mahsulot_nomi")
#         miqdor = cleaned_data.get("miqdor")
#         amaliyot_turi = cleaned_data.get("amaliyot_turi")
#         olchov_birligi = cleaned_data.get("olchov_birligi")
#
#         # Agar miqdor 0 bo'lsa, xatolik chiqarish
#         if miqdor == 0:
#             raise ValidationError({"count": "Mahsulot soni 0 bo'lishi mumkin emas!"})
#
#         # Ombordagi mahsulot miqdorini tekshirish
#         if amaliyot_turi == "Chiqdi":
#             mahsulot_balans = MahsulotBalans.objects.filter(mahsulot_nomi=mahsulot_nomi).first()
#             if not mahsulot_balans:  # Agar mahsulot mavjud bo'lmasa
#                 raise ValidationError({"product_id": "Bu mahsulot omborda mavjud emas!"})
#             if miqdor > mahsulot_balans.qoldiq:  # Agar mahsulot yetarli bo'lmasa
#                 raise ValidationError({"count": "Omborda yetarli mahsulot mavjud emas!"})
#             # Kirim va chiqimdagi o'lchov birligini tekshirish
#             oxirgi_kiruv = MahsulotBalansTarix.objects.filter(
#                 mahsulot_nomi=mahsulot_nomi, type_id="Kirdi"
#             ).last()  # So'nggi kirimni olish
#
#             if oxirgi_kiruv and oxirgi_kiruv.olchov_birligi != olchov_birligi:
#                 raise ValidationError(
#                     {"measurement_id": "Kiritilgan o'lchov birligi so'nggi kirimdagi o'lchov birligiga mos kelmaydi!"}
#                 )
#         return cleaned_data
