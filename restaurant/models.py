from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError


class Article(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    preview_image = models.ImageField(null=True, blank=True, max_length=255)
    content = models.TextField()
    show_at_index = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    modified_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "칼럼"
        verbose_name_plural = "칼럼s"

    def __str__(self):

        return f"{self.id} - {self.title}"


class Restaurant(models.Model):
    name = models.CharField("이름", max_length=100, db_index=True)
    branch_name = models.CharField(
        "지점", max_length=100, db_index=True, null=True, blank=True
    )
    description = models.TextField("설명", null=True, blank=True)
    address = (models.CharField("주소", max_length=255, db_index=True),)
    feature = models.CharField("특징", max_length=255, null=True, blank=True)
    is_closed = models.BooleanField("폐업여부", default=False)
    latitude = models.DecimalField(
        "위도",
        max_digits=16,  # 소수점포함 숫자자릿점
        decimal_places=12,  # 소수점 이하 자릿수 정수부: 소수부
        db_index=True,
        default="0.0000",
    )
    longitude = models.DecimalField(
        "경도",
        max_digits=16,
        decimal_places=12,
        db_index=True,
        default="0.0000",
    )
    phone = models.CharField("전화번호", max_length=16, help_text="E.164 vhaot:")
    rating = models.DecimalField(
        "평점",
        max_digits=3,
        decimal_places=2,
        default=0.0,
    )
    rating_count = models.PositiveIntegerField(
        "평가수",
        default=0,
    )
    start_time = models.TimeField("영업시작시간", null=True, blank=True)
    end_time = models.TimeField("영업종료시간", null=True, blank=True)
    last_order_time = models.TimeField("주문마감시간", null=True, blank=True)
    category = models.ForeignKey(
        "RestaurantCategory",
        on_delete=models.SET_NULL,  # 참조된 카테고리 삭제시 null로 설정 (데이터 보존)
        blank=True,
        null=True,
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
    )  # M:N 관계(다대다)
    region = models.ForeignKey(
        "Region",
        on_delete=models.SET_NULL,  # 참조된 wldur 삭제시 null로 설정 (데이터 보존)
        null=True,
        blank=True,
        db_index=True,
        verbose_name="지역",
        related_name="restaurants",  # 역참조 이름 설정
    )
    # 레스토랑 지역 region.restaurants.all()

    class Meta:
        verbose_name = "레스토랑"
        verbose_name_plural = "레스토랑s"

    def __str__(self):
        return f"{self.name} {self.branch_name}" if self.branch_name else self.name

    # 지점명이 있으면 이름,지점명을 반환해주고, 없으면 이름만 반환


class CuisineType(models.Model):
    name = models.CharField("이름", max_length=20)

    class Meta:
        verbose_name = "음식종류"
        verbose_name_plural = "음식종류s"

    def __str__(self):
        return self.name


class RestaurantCategory(models.Model):
    name = models.CharField("이름", max_length=20)
    cuisineType = models.ForeignKey(
        "CuisineType", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

    def __str__(self):
        return self.name


class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    is_representative = models.BooleanField(
        "대표 이미지 여부", default=False
    )  # 대표 이미지
    order = models.PositiveIntegerField("순서", null=True, blank=True)
    Name = models.CharField("이름", max_length=100, null=True, blank=True)
    image = models.ImageField("이미지", max_length=100, upload_to="restaurant")
    # 이미지 업로드시 MEDIA_ROOT/restaurant/폴더 아래 파일이 저장

    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

    def __str__(self):
        return f"{self.id}:{self.image}"

    # 대표이미지를 2개 이상 저장하지 못하도록 막는 코드
    def clean(self):
        images = self.restaurant.restaurantimage_set.filter(is_representative=True)
        # .restaurantimage_set: 해당 Restaurant에 연결된 모든 이미지들
        # .filter() : 괄호안의 조건에 따라 맞게 필터링한 이미지를 가져온다.

        if self.is_representative and images.exclude(id=self.id).count() > 0:
            raise ValidationError("대표이미지는 한개만 설정 가능합니다.")
        # 현재 이미지가 대표 이미지고 그외의 이미지가 1개 이상 존재한다면 경고문을 띄운다


class RestaurantMenu(models.Model):

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    Name = models.CharField("이름", max_length=100)
    price = models.PositiveIntegerField("가격", default=0)
    image = models.ImageField(
        "이미지", upload_to="restaurant-menu", null=True, blank=True
    )  # MEDIA_ROOT/restaurant-menu/이미지파일을 저장
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "레스토랑 메뉴"
        verbose_name_plural = "레스토랑 메뉴s"

    def __str__(self):
        return f"{self.id}:{self.image}"


class Review(models.Model):
    title = models.CharField("제목", max_length=100)
    author = models.CharField("작성자", max_length=100)
    profile_image = models.ImageField(
        "이미지", upload_to="restaurant-menu", null=True, blank=True
    )
    content = models.TextField("내용")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # 양의 정수로 min(1) 부터 max(5)의 범위를 가진다. (시스템상 최대 허용 범위(0~ 30,000))
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    social_channel = models.ForeignKey(
        "SocialChannel", on_delete=models.SET_NULL, blank=True, null=True
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "리뷰"
        verbose_name_plural = "리뷰s"

    def __str__(self):
        return f"{self.author}:{self.title}"

    # -------------------------------------------------------
    @property
    def restaurant_name(self):
        return self.restaurant.name

    @property
    def content_partial(self):
        return self.content[:20]


# -------------------------------------------------------


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(max_length=100, upload_to="review")
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "리뷰이미지"
        verbose_name_plural = "리뷰이미지"

    def __str__(self):
        return f"{self.id}:{self.image}"


class SocialChannel(models.Model):
    name = models.CharField("이름", max_length=100)

    class Meta:
        verbose_name = "소셜채널"
        verbose_name_plural = "소셜채널"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        "이름", max_length=100, unique=True
    )  # 이 필드는 중복을 허용하지 않음

    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그"

    def __str__(self):
        return self.name


class Region(models.Model):
    sido = models.CharField("광역시도", max_length=20)
    sigungu = models.CharField("시군구", max_length=20)
    eupmyeondong = models.CharField("읍면동", max_length=20)

    class Meta:
        verbose_name = "지역"
        verbose_name_plural = "지역"
        unique_together = ("sido", "sigungu", "eupmyeondong")

    def __str__(self):
        return f"{self.sido} {self.sigungu} {self.eupmyeondong}"
