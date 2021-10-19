<h1 align="center">API для сайта знакомств (+ парсинг товаров с сайта Citilink</h1>


<h2 align="center"> 1. Создать модель участников. У участника должна быть аватарка, пол, имя и фамилия, почта. </h2>

<p> Для начала создана модель участников которая унаследованная от класса AbtractBaseUser. К которой разработан менеджер который предоставляет функцию для создания участника по введенным данным и хэширования пароля. </p>

* Модель участников

```
class User(AbstractBaseUser):
    """ Модель участников которая создана на основе пользовательской модели """

    class GenderChoice(models.TextChoices):
        MALE = "М", _("Мужской")
        FEMALE = "Ж", _("Женский")

    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя участника")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Фамилия участника")
    gender = models.CharField(max_length=20, null=True, blank=True,
                              choices=GenderChoice.choices, verbose_name="Пол участника")
    email = models.EmailField(unique=True, verbose_name="Электронный адрес участника")
    avatar = models.ImageField(upload_to="participants/avatar/", blank=True, null=True,
                               verbose_name="Аватар участника")
    longitude = models.FloatField(max_length=255, null=True, blank=True, verbose_name="Долгота")
    latitude = models.FloatField(max_length=255, null=True, blank=True, verbose_name="Широта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регестрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    is_active = models.BooleanField(default=True, verbose_name="Статус активности")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ к админ панели")
    is_admin = models.BooleanField(default=False, verbose_name="Права администратора")

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender', 'avatar']

    objects = UserManager()

```
* Менеджер дл модели участников

```

class UserManager(BaseUserManager):
    """ Менеджер для модели участников """

    def create_user(self, email, first_name, last_name, gender, avatar,
                    password=None, is_staff=False, is_admin=False, is_activate=True):
        # Общая функция при создании участника
        if not email:
            raise ValueError("У участника должен быть электронная почта")
        if not first_name:
            raise ValueError("У участника должно быть имя")
        if not last_name:
            raise ValueError("У участника должна быть фамилия")
        if not password:
            raise ValueError('У участника должен быть пароль')
        user_obj = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            avatar=avatar,
        )
        user_obj.set_password(password)
        user_obj.is_staff = is_staff
        user_obj.is_admin = is_admin
        user_obj.is_activate = is_activate
        user_obj.save(using=self.db)
        return user_obj

```

<h2 align="center"> 2. Создать эндпоинт регистрации нового участника: /api/clients/create (не забываем о пароле и совместимости с авторизацией модели участника) </h2>

<p> Создан класс сериализатор для созданной модели участников. После чего в представлении создан класс унаследованный от CreateAPIView с помощью которого при введенным данных участника будет создана запись в БД.  </p>

* Сериализатор

```
class UserRegisterSerializers(serializers.ModelSerializer):
    """ Класс сериализатора для регистрации участника в системе. """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'longitude', 'latitude', 'gender', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

```

* Класс в файле представлений для регестрации участника
```

class UserCreate(generics.CreateAPIView):
    """ Класс Generics с помощью которого происходит регистрация участника. """
    queryset = User
    serializer_class = UserRegisterSerializers
    permission_classes = (AllowAny, )

```

<h2 align="center"> 3. При регистрации нового участника необходимо обработать его аватарку: наложить на него водяной знак (в качестве водяного знака можете взять любую картинку).
 </h2>
 
 <p> Для отслежки аватара при регестрации был переопределен метод save в котором берется случайная картинка и с помощьюю бибилотеки Pillow происходит наложения водяного знака. <p>

* Переопределение метода save

```
      def save(self, *args, **kwargs):
        if self.avatar:
            img = Image.open(self.avatar)
            watermark = Image.open('/home/leom/PycharmProjects/suddenMeetProject/pepe.png')
            img.paste(watermark, (0,0))
            output = BytesIO()
            img.save(output, 'PNG', optimize=True)
            output.seek(0)
            self.avatar.file = output
        super().save(*args, **kwargs)
```
* Результат обработки аватарки

![Тестовая аватарка](https://github.com/LeonMaxwell/sudden-meet-project/blob/main/photo_2021-07-27_02-36-38.jpg)

<h2 align="center"> 4. Создать эндпоинт оценивания участником другого участника: /api/clients/{id}/match. В случае, если возникает взаимная симпатия, то ответом выдаем почту клиенту и отправляем на почты участников: «Вы понравились <имя>! Почта участника: <почта>».</h2>

  <p> Для отслеживания информации о взаимности участников была создана модель которая хранит информацию о том какой участник оценил другого участника. Так же в предстовлении была создана функция которая отслеживает и позволет оценивать участников с некоторыми ограничениями. В виде запрета оценивани самого себя или повторное оценивание участников. После успешной проверки создается запись в базе о том кто кого оценил. Если это взаимно используя средства django отправляются сообщения обоим участникам. </p>
  
* Модель хранения информации симпатий c методом по отправке сообщений на почту.
```
  class MatchSudden(models.Model):
    """ Класс для сбора данных о симпатиях участников. """
    mover = models.OneToOneField(User, related_name='mover', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Участник")
    simpy = models.OneToOneField(User, related_name='simpy', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Симпатия")

    def __str__(self):
        return f"{self.mover.first_name} оценил {self.simpy.first_name}"

    def mutual_sympathy(self):
        # Метод проверки на взаимную симпатию
        all_match = MatchSudden.objects.all()
        try:
            all_match.get(mover=self.simpy, simpy=self.mover)
            message1 = ('Взаимность', f'Вы понравились {self.simpy.first_name}! Почта участника: {self.simpy.email}',
                        'localhost@gmail.com', [self.mover.email])
            message2 = ('Взаимность', f'Вы понравились {self.mover.first_name}! Почта участника: {self.mover.email}',
                        'java.leon@mail.ru', [self.simpy.email])
            send_mass_mail((message1, message2), fail_silently=False)
            return "Ого это взаимно нечего себе!"
        except ObjectDoesNotExist:
            return "Надеюсь это будет взаимно"
```

* Функция в предсавлении для обмена симпатиями между участниками
```
  @api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def grading(request, pk):
    # Реализация обмена симпатиями между участниками
    mover = get_object_or_404(User, pk=request.user.pk)
    matcher = get_object_or_404(User, pk=pk)
    if request.method == "GET":
        if request.user.pk == id:
            return Response("Вы самолюб! :)")
        else:
            try:
                suden = MatchSudden()
                suden.mover = mover
                suden.simpy = matcher
                respon = suden.mutual_sympathy()
                suden.save()
            except IntegrityError as e:
                respon = "Вы уже оценили этого участника"
            return Response(respon)
```


<h2 align="center"> 5. Создать эндпоинт списка участников: /api/list. Должна быть возможность фильтрации листа по полу, имени, фамилии. Советую использовать библиотеку Django-filters.</h2>

  <p> В представлении был реализован класс унаследованный от ListAPIView. Данный класс выводит информацию о участникахх. Для разработки филтров была использована библиотека django-filter. Для этого был создан класс который реализует фильтрацию по полу, имени и фамилии. </p>
 
* Класс в представлении для вывода информации об участниках

```
  class UserListView(generics.ListAPIView):
    """ Класс для генерации списка из все участников. С фильтрацией по поле, имени и фамилии. """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializers
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter
  
```

* Класс филтра
```
  class EmployeeFilter(filters.FilterSet):
    """ Класс который подключает фильтрацию. """

    class Meta:
        model = User
        fields = ['gender', 'first_name', 'last_name']
  
```
<h2 align="center"> 6. Реализовать определение дистанции между участниками. Добавить поля долготы и широты. В api списка добавить дополнительный фильтр, который бы показывал участников в пределах заданной дистанции. </h2>

  <p> Был создан собственный фильтр который по введенным данным получает расстояние между участниками и выводит если участник попадает в заданную дистанцию. Для релизации формулы был использован инструмент Django RawSQL. Для того что бы sqlite понимала математические операции был разработан сигнал. После чего была созданна аннотация distance для всех пользователей по которой собстенно и произодится фильтрация. </p>

* Доработанный класс фильтров дл обработки своей фильтрации
  
```
  class EmployeeFilter(filters.FilterSet):
    """ Класс который подключает фильтрацию. """
    distance = filters.CharFilter(method='filter_queryset', label="Дистанция")

    class Meta:
        model = User
        fields = ['gender', 'first_name', 'last_name']

    def filter_queryset(self, queryset):
        queryset = User.objects.all()
        user_id = self.request.user.pk
        distance = self.request.query_params.get('distance')
        if user_id and distance:
            user = get_object_or_404(User, id=user_id)
            queryset = get_locations_nearby_coords(user.latitude, user.longitude, int(distance))
        return queryset
```
* Функция по расчету дистанции
```
 def get_locations_nearby_coords(latitude, longitude, max_distance=None):
    """
    Return objects sorted by distance to specified coordinates
    which distance is less than max_distance given in kilometers
    """
    # Great circle distance formula
    gcd_formula = "6371 * acos(least(greatest(\
    cos(radians(%s)) * cos(radians(latitude)) \
    * cos(radians(longitude) - radians(%s)) + \
    sin(radians(%s)) * sin(radians(latitude)) \
    , -1), 1))"
    distance_raw_sql = RawSQL(
        gcd_formula,
        (latitude, longitude, latitude)
    )
    qs = User.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
    if max_distance is not None:
        qs = qs.filter(distance__lt=max_distance)
    return qs
  
```

* Сигнал для sqlite


  
```
  @receiver(connection_created)
def extend_sqlite(connection=None, **kwargs):
    if connection.vendor == "sqlite":
        # sqlite не понимает матиматические операции, поэтому добавим ей эту возможность
        cf = connection.connection.create_function
        cf('acos', 1, math.acos)
        cf('cos', 1, math.cos)
        cf('radians', 1, math.radians)
        cf('sin', 1, math.sin)
        cf('least', 2, min)
        cf('greatest', 2, max)
  
```

<h2 align="center"> 7. Создать модуль products и напарсить товаров с https://www.citilink.ru/ . Парсим категорию (должно быть отдельным объектом в базе и учтены связи с родителями/детьми), цену, название и картинку </h2>

  <p> Для начала были реализованны модели с каталогом, катигорией и самим продуктом с соответстующими полями. После чего был разработан класс который для начала подключался к сайту и парсил названия каталогогов и категорий с ссылками. Дальше используя полученные ссылки получал данные о товарах такие как название товара, фото товара и его цена. Все это записывается в словарь. После чего с каждым из каталогов, категорий и товаров записываются в базу данных. </p>
  
 * Классы каталогов, категроий и товаров
```
  class Catalog(models.Model):
    name_catalog = models.CharField(max_length=255, verbose_name="Название каталога", null=True, blank=True)

    class Meta:
        verbose_name = "Каталог"
        verbose_name_plural = "Каталоги"

    def __str__(self):
        return self.name_catalog


class Category(models.Model):
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Каталог")
    name_category = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название каталога")

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return f'{self.name_category} из каталога {self.catalog.name_catalog}'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name="Категория товара")
    name_product = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название продукта")
    photo_product = models.ImageField(upload_to="media/product/", blank=True, null=True, verbose_name="Фото товара")
    price_product = models.CharField(max_length=255, null=True, blank=True, verbose_name="Цена товара")

    class Meta:
        verbose_name = "Информация продукта"
        verbose_name_plural = "Информация о продуктах"

    def __str__(self):
        return self.name_product
``` 
