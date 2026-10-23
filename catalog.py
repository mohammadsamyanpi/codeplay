"""Bilingual lesson content. Solutions never ship as public static files."""


def bi(en, fa):
    return {"en": en, "fa": fa}


LESSONS = []


def lesson(track, topic, kind, title, prompt, code, answer, explanation, hint, options=None):
    item = dict(id=f"{track}-{len([x for x in LESSONS if x['track'] == track]) + 1:02d}",
                track=track, topic=topic, kind=kind, title=bi(*title), prompt=bi(*prompt),
                code=code, answer=answer, explanation=bi(*explanation), hint=bi(*hint), xp=50)
    if options:
        item["options"] = options
    LESSONS.append(item)


lesson('free', 'python', 'quiz', ('Your first print', 'اولین چاپ'),
       ('Which line prints Hello?', 'کدام خط Hello را چاپ می‌کند؟'), '', 'print("Hello")',
       ('print() displays a value; text belongs inside quotes.', 'تابع print مقدار را نمایش می‌دهد؛ متن داخل کوتیشن قرار می‌گیرد.'),
       ('Choose a function call with quoted text.', 'فراخوانی تابع با متن داخل کوتیشن را انتخاب کن.'),
       ['print("Hello")', 'echo("Hello")', 'print Hello', 'Hello.print()'])
lesson('free', 'python', 'blank', ('Name your adventurer', 'نام ماجراجو'),
       ('Fill the gap to store Alex in name.', 'جای خالی را پر کن تا Alex در متغیر name ذخیره شود.'),
       'name ___ "Alex"\nprint(name)', ['='],
       ('Assignment uses =, while == compares values.', 'انتساب با = انجام می‌شود؛ == برای مقایسه است.'), ('Use the assignment operator.', 'از عملگر انتساب استفاده کن.'))
lesson('free', 'python', 'output', ('Count your coins', 'شمارش سکه‌ها'),
       ('What is printed?', 'چه چیزی چاپ می‌شود؟'), 'coins = 4\nprint(coins + 3)', ['7'],
       ('4 + 3 evaluates to 7.', 'حاصل ۴ + ۳ برابر ۷ است.'), ('Add the two numbers.', 'دو عدد را جمع کن.'))
lesson('free', 'python', 'debug', ('Repair the greeting', 'اصلاح پیام خوشامد'),
       ('Choose the corrected line.', 'خط اصلاح‌شده را انتخاب کن.'), 'print("Hello)', 'print("Hello")',
       ('The opening and closing quotes must match.', 'کوتیشن آغاز و پایان باید با هم مطابقت داشته باشند.'),
       ('Check the closing quote.', 'کوتیشن پایانی را بررسی کن.'), ['print("Hello")', 'print(Hello)', 'print("Hello)', 'print["Hello"]'])
lesson('free', 'python', 'quiz', ('Text or number?', 'متن یا عدد؟'),
       ('Which value is a string?', 'کدام مقدار رشته است؟'), '', '"42"',
       ('Quotes make "42" text, even though it contains digits.', 'کوتیشن، "42" را به متن تبدیل می‌کند، حتی اگر شامل رقم باشد.'),
       ('Look for quotes.', 'به دنبال کوتیشن بگرد.'), ['42', '"42"', '4.2', 'True'])
lesson('free', 'python', 'blank', ('Measure a word', 'اندازه‌ی یک واژه'),
       ('Complete the function that counts characters.', 'تابعی را کامل کن که تعداد نویسه‌ها را می‌شمارد.'), 'print(___("Python"))', ['len'],
       ('len("Python") is 6.', 'خروجی len("Python") برابر ۶ است.'), ('The function name has three letters.', 'نام تابع سه حرف دارد.'))
lesson('free', 'python', 'output', ('Repeat a spell', 'تکرار جادو'),
       ('Write the output without quotes.', 'خروجی را بدون کوتیشن بنویس.'), 'print("ha" * 3)', ['hahaha'],
       ('Multiplying a string repeats it.', 'ضرب رشته در عدد، آن رشته را تکرار می‌کند.'), ('Join three copies of ha.', 'سه ha را پشت سر هم قرار بده.'))
lesson('free', 'python', 'quiz', ('Choose a condition', 'انتخاب شرط'),
       ('Which comparison checks whether score is at least 10?', 'کدام مقایسه بررسی می‌کند امتیاز حداقل ۱۰ است؟'), 'score = 12', 'score >= 10',
       ('>= means greater than or equal to.', 'علامت >= یعنی بزرگ‌تر یا مساوی.'), ('Include the boundary value 10.', 'مقدار مرزی ۱۰ را هم در نظر بگیر.'),
       ['score > 10', 'score >= 10', 'score = 10', 'score < 10'])
lesson('free', 'python', 'blank', ('An alternative path', 'مسیر جایگزین'),
       ('Complete the branch used when the condition is false.', 'شاخه‌ای را کامل کن که در صورت نادرست بودن شرط اجرا می‌شود.'),
       'if coins > 5:\n    print("Buy")\n___:\n    print("Save")', ['else'],
       ('else runs when the if condition is false.', 'وقتی شرط if نادرست باشد، else اجرا می‌شود.'), ('It pairs with if.', 'این واژه همراه if استفاده می‌شود.'))
lesson('free', 'python', 'debug', ('Indent the path', 'تورفتگی مسیر'),
       ('Choose the correct block.', 'بلوک صحیح را انتخاب کن.'), 'if True:\nprint("Go")', 'if True:\n    print("Go")',
       ('Python uses indentation to group a block.', 'پایتون از تورفتگی برای مشخص کردن بلوک استفاده می‌کند.'), ('The body needs indentation.', 'بدنه باید تورفتگی داشته باشد.'),
       ['if True:\n    print("Go")', 'if True\n    print("Go")', 'if True:\nprint("Go")', 'if True; print("Go")'])
lesson('free', 'python', 'output', ('Read the backpack', 'خواندن کوله‌پشتی'),
       ('What is printed?', 'چه چیزی چاپ می‌شود؟'), 'bag = ["key", "map", "coin"]\nprint(bag[1])', ['map'],
       ('List indexes start at zero; index 1 is the second item.', 'شماره‌گذاری لیست از صفر شروع می‌شود؛ اندیس ۱ عنصر دوم است.'), ('Start counting at zero.', 'شمردن را از صفر آغاز کن.'))
lesson('free', 'python', 'blank', ('Add a key', 'اضافه کردن کلید'),
       ('Complete the list method.', 'متد لیست را کامل کن.'), 'bag = []\nbag.___("key")\nprint(bag)', ['append'],
       ('append adds one item at the end of a list.', 'متد append یک عنصر به انتهای لیست اضافه می‌کند.'), ('Use the method for adding one item.', 'متد اضافه کردن یک عنصر را بنویس.'))
lesson('free', 'python', 'order', ('Build a loop', 'ساخت حلقه'),
       ('Arrange the lines to print each item.', 'خطوط را مرتب کن تا هر عنصر چاپ شود.'), '', [0, 1, 2],
       ('Create the list, start the loop, then indent its body.', 'ابتدا لیست، سپس حلقه و بعد بدنه‌ی دارای تورفتگی را بنویس.'),
       ('The list must exist before the loop.', 'لیست باید پیش از حلقه ساخته شده باشد.'), ['items = [1, 2]', 'for item in items:', '    print(item)'])
lesson('free', 'python', 'output', ('Three steps', 'سه قدم'),
       ('Write each printed number on a separate line.', 'هر عدد چاپ‌شده را در خط جداگانه بنویس.'), 'for n in range(3):\n    print(n)', ['0\n1\n2'],
       ('range(3) gives 0, 1, 2; the stop value is excluded.', 'range(3) مقادیر ۰، ۱ و ۲ را می‌دهد؛ حد پایانی شامل نمی‌شود.'), ('Start at zero and stop before three.', 'از صفر شروع کن و پیش از سه توقف کن.'))
lesson('free', 'python', 'blank', ('Create a function', 'ساخت تابع'),
       ('Complete the function definition.', 'تعریف تابع را کامل کن.'), '___ greet():\n    print("Hi")\ngreet()', ['def'],
       ('def introduces a function definition.', 'واژه‌ی def تعریف تابع را آغاز می‌کند.'), ('Use the function definition keyword.', 'واژه‌ی کلیدی تعریف تابع را بنویس.'))
lesson('free', 'python', 'quiz', ('Return a result', 'برگرداندن نتیجه'),
       ('Which line returns the sum to the caller?', 'کدام خط مجموع را به فراخواننده برمی‌گرداند؟'), 'def add(a, b):\n    # next line', 'return a + b',
       ('return sends a result back; print only displays it.', 'return نتیجه را برمی‌گرداند؛ print فقط آن را نمایش می‌دهد.'), ('Displaying and returning are different.', 'نمایش دادن با برگرداندن فرق دارد.'),
       ['print(a + b)', 'return a + b', 'a + b = return', 'break'])
lesson('free', 'python', 'output', ('Call your function', 'فراخوانی تابع'),
       ('What is printed?', 'چه چیزی چاپ می‌شود؟'), 'def double(n):\n    return n * 2\nprint(double(6))', ['12'],
       ('The argument 6 replaces n, so the result is 12.', 'آرگومان ۶ جای n قرار می‌گیرد و نتیجه ۱۲ می‌شود.'), ('Substitute 6 for n.', 'به جای n عدد ۶ بگذار.'))
lesson('free', 'python', 'blank', ('Read a dictionary', 'خواندن دیکشنری'),
       ('Fill the gap with a quoted key to print Mina.', 'کلید داخل کوتیشن را بنویس تا Mina چاپ شود.'), 'user = {"name": "Mina"}\nprint(user[___])', ['"name"', "'name'"],
       ('A dictionary retrieves values using keys.', 'دیکشنری مقدارها را با کلید بازیابی می‌کند.'), ('The only key is name.', 'تنها کلید name است.'))
lesson('free', 'python', 'debug', ('Convert before adding', 'تبدیل پیش از جمع'),
       ('Choose the expression that prints 12.', 'عبارتی را انتخاب کن که ۱۲ چاپ می‌کند.'), 'age = "10"\nprint(age + 2)', 'print(int(age) + 2)',
       ('int converts numeric text to an integer.', 'تابع int متن عددی را به عدد صحیح تبدیل می‌کند.'), ('Convert age to a number first.', 'ابتدا age را به عدد تبدیل کن.'),
       ['print(age + "2")', 'print(int(age) + 2)', 'print(str(age) + 2)', 'print(age * 2)'])
lesson('free', 'python', 'project', ('Mini project: coin counter', 'پروژه‌ی کوچک: شمارنده‌ی سکه'),
       ('Fill both gaps to sum the coins and print 10.', 'دو جای خالی را پر کن تا مجموع سکه‌ها محاسبه و ۱۰ چاپ شود.'),
       'coins = [2, 3, 5]\ntotal = 0\nfor coin in coins:\n    total ___ coin\n___(total)', [['+='], ['print']],
       ('The loop adds each coin to total, then print displays the result.', 'حلقه هر سکه را به total اضافه می‌کند و print نتیجه را نمایش می‌دهد.'),
       ('Use an addition assignment and an output function.', 'از انتساب جمع و تابع نمایش خروجی استفاده کن.'))
lesson('free', 'django', 'quiz', ('What is Django?', 'جنگو چیست؟'),
       ('Choose the best description of Django.', 'بهترین توضیح جنگو را انتخاب کن.'), '', 'web',
       ('Django is a Python framework for building web applications.', 'جنگو چارچوبی در پایتون برای ساخت برنامه‌های وب است.'), ('Think about websites.', 'به وب‌سایت‌ها فکر کن.'),
       [bi('web', 'web'), bi('A Python web framework', 'چارچوب وب پایتون')])
# Replace the previous options with stable machine values and translated labels.
LESSONS[-1]['options'] = [dict(value='web', label=bi('A Python web framework', 'چارچوب وب پایتون')), dict(value='editor', label=bi('A text editor', 'ویرایشگر متن')), dict(value='os', label=bi('An operating system', 'سیستم‌عامل')), dict(value='language', label=bi('A separate programming language', 'یک زبان برنامه‌نویسی جدا'))]
lesson('free', 'django', 'quiz', ('Request and response', 'درخواست و پاسخ'),
       ('What does a browser send to a web server?', 'مرورگر چه چیزی به وب‌سرور می‌فرستد؟'), '', 'request',
       ('The browser sends an HTTP request; the server returns a response.', 'مرورگر درخواست HTTP می‌فرستد و سرور پاسخ برمی‌گرداند.'), ('It asks the server for a resource.', 'مرورگر یک منبع را از سرور درخواست می‌کند.'),
       [dict(value='request', label=bi('A request', 'درخواست')), dict(value='database', label=bi('A database', 'پایگاه داده')), dict(value='model', label=bi('A model', 'مدل')), dict(value='password', label=bi('Every saved password', 'همه‌ی رمزهای ذخیره‌شده'))])
lesson('free', 'django', 'quiz', ('The big picture', 'تصویر کلی جنگو'),
       ('Which component describes stored data?', 'کدام بخش ساختار داده‌های ذخیره‌شده را توصیف می‌کند؟'), '', 'Model',
       ('Models describe data; views handle requests; templates describe presentation.', 'مدل‌ها داده، ویوها پردازش درخواست و قالب‌ها نمایش را توصیف می‌کنند.'),
       ('Think of the data layer.', 'به لایه‌ی داده فکر کن.'), ['Model', 'Template', 'CSS', 'Browser'])
lesson('free', 'django', 'quiz', ('When to use Django', 'چه زمانی از جنگو استفاده کنیم؟'),
       ('Which project is a good fit for Django?', 'کدام پروژه برای جنگو مناسب است؟'), '', 'site',
       ('A site with accounts and stored posts benefits from a web framework.', 'وب‌سایتی با حساب کاربری و نوشته‌های ذخیره‌شده از چارچوب وب بهره می‌برد.'), ('Look for server-side data.', 'به دنبال داده‌های سمت سرور باش.'),
       [dict(value='site', label=bi('A blog with user accounts', 'وبلاگ با حساب کاربری')), dict(value='font', label=bi('A font file', 'فایل فونت')), dict(value='image', label=bi('A single photo', 'یک عکس')), dict(value='cable', label=bi('A network cable', 'کابل شبکه'))])

lesson('pro', 'python', 'blank', ('List comprehensions', 'خلاصه‌نویسی لیست'),
       ('Complete the keyword to double each number.', 'واژه را کامل کن تا هر عدد دو برابر شود.'), 'doubles = [n * 2 ___ n in range(4)]', ['for'],
       ('A comprehension combines an expression and a for clause.', 'خلاصه‌نویسی لیست از عبارت و بخش for تشکیل می‌شود.'), ('Use a loop keyword.', 'واژه‌ی حلقه را بنویس.'))
lesson('pro', 'python', 'output', ('Filter a list', 'فیلتر کردن لیست'),
       ('Write the printed list.', 'لیست چاپ‌شده را بنویس.'), 'print([n for n in range(5) if n % 2 == 0])', ['[0, 2, 4]'],
       ('Only numbers with remainder zero when divided by 2 remain.', 'فقط عددهایی باقی می‌مانند که با تقسیم بر ۲ باقیمانده‌ی صفر دارند.'), ('Zero is even too.', 'صفر هم زوج است.'))
lesson('pro', 'python', 'blank', ('Handle invalid input', 'مدیریت ورودی نامعتبر'),
       ('Name the exception raised here.', 'نام استثنای ایجادشده را بنویس.'), 'try:\n    int("hello")\nexcept ___:\n    print("Invalid")', ['ValueError'],
       ('int cannot parse hello and raises ValueError.', 'تابع int نمی‌تواند hello را تبدیل کند و ValueError ایجاد می‌کند.'), ('The type is valid, but its value is unsuitable.', 'نوع درست است ولی مقدار مناسب نیست.'))
lesson('pro', 'python', 'order', ('A small class', 'یک کلاس کوچک'),
       ('Arrange the class, method and body.', 'کلاس، متد و بدنه را مرتب کن.'), '', [0, 1, 2],
       ('The method belongs inside the class, and its body inside the method.', 'متد داخل کلاس و بدنه داخل متد قرار می‌گیرد.'), ('Indentation shows nesting.', 'تورفتگی تودرتویی را نشان می‌دهد.'),
       ['class Hero:', '    def greet(self):', '        return "Hello"'])
lesson('pro', 'python', 'debug', ('Avoid shared defaults', 'پرهیز از مقدار پیش‌فرض مشترک'),
       ('Choose the safer default for a mutable list parameter.', 'مقدار پیش‌فرض امن‌تر برای پارامتر لیست را انتخاب کن.'), 'def collect(items=[]):\n    items.append("coin")\n    return items', 'None',
       ('Use None, then create a new list inside the function when needed.', 'از None استفاده کن و در صورت نیاز داخل تابع یک لیست تازه بساز.'), ('Do not reuse one list across calls.', 'یک لیست را بین فراخوانی‌ها مشترک نکن.'), ['None', '[]', '{}', 'list()'])
lesson('pro', 'python', 'project', ('Mini project: inventory', 'پروژه‌ی کوچک: موجودی'),
       ('Complete the dictionary update and return statement.', 'به‌روزرسانی دیکشنری و عبارت برگرداندن را کامل کن.'),
       'def add_coin(bag):\n    bag["coin"] = bag.___("coin", 0) + 1\n    ___ bag', [['get'], ['return']],
       ('get supplies a default for a missing key; return sends the updated bag back.', 'متد get برای کلید ناموجود مقدار پیش‌فرض می‌دهد و return کوله‌ی به‌روز را برمی‌گرداند.'),
       ('Use a dictionary lookup with a default.', 'از خواندن دیکشنری با مقدار پیش‌فرض استفاده کن.'))
lesson('pro', 'django', 'quiz', ('Start a Django project', 'شروع پروژه‌ی جنگو'),
       ('Which command creates a project named config?', 'کدام دستور پروژه‌ای به نام config می‌سازد؟'), '', 'django-admin startproject config',
       ('startproject creates project configuration; startapp creates an app.', 'دستور startproject تنظیمات پروژه و startapp یک اپ می‌سازد.'), ('Create the project before its apps.', 'پروژه را پیش از اپ‌هایش بساز.'),
       ['django-admin startproject config', 'django-admin startapp config', 'python config.py', 'pip start config'])
lesson('pro', 'django', 'blank', ('Create an app', 'ساخت اپ'),
       ('Complete the command for a blog app.', 'دستور ساخت اپ blog را کامل کن.'), 'python manage.py ___ blog', ['startapp'],
       ('startapp generates a Django application skeleton.', 'دستور startapp ساختار اولیه‌ی یک اپ جنگو را می‌سازد.'), ('It is not startproject.', 'این دستور startproject نیست.'))
lesson('pro', 'django', 'blank', ('Return an HTTP response', 'برگرداندن پاسخ HTTP'),
       ('Complete the response class.', 'کلاس پاسخ را کامل کن.'), 'from django.http import HttpResponse\n\ndef home(request):\n    return ___("Hello")', ['HttpResponse'],
       ('A view returns a response object.', 'ویو یک شیء پاسخ برمی‌گرداند.'), ('Use the imported class.', 'از کلاس واردشده استفاده کن.'))
lesson('pro', 'django', 'quiz', ('Route to a view', 'اتصال مسیر به ویو'),
       ('Choose a route that passes the home function to Django.', 'مسیری را انتخاب کن که تابع home را به جنگو می‌دهد.'), 'from django.urls import path\nfrom . import views', 'path("", views.home)',
       ('Pass the function itself; Django calls it for each request.', 'خود تابع را بده؛ جنگو آن را برای هر درخواست فراخوانی می‌کند.'), ('Do not call home while defining the URL.', 'هنگام تعریف مسیر، home را فراخوانی نکن.'),
       ['path("", views.home)', 'path("", views.home())', 'path(views.home, "")', 'route("", home)'])
lesson('pro', 'django', 'blank', ('Render a template', 'نمایش قالب'),
       ('Complete the shortcut for rendering HTML.', 'تابع میانبر نمایش HTML را کامل کن.'), 'from django.shortcuts import render\n\ndef home(request):\n    return ___(request, "home.html", {"name": "Mina"})', ['render'],
       ('render combines a template and context into an HTTP response.', 'تابع render قالب و داده‌های context را در یک پاسخ HTTP ترکیب می‌کند.'), ('Use the imported shortcut.', 'از تابع میانبر واردشده استفاده کن.'))
lesson('pro', 'django', 'blank', ('Template variables', 'متغیرهای قالب'),
       ('Write the variable name inside the template expression.', 'نام متغیر را داخل عبارت قالب بنویس.'), '<h1>Hello, {{ ___ }}</h1>\n<!-- context: {"name": "Mina"} -->', ['name'],
       ('Double braces display a context variable, escaped by default.', 'آکولادهای دوتایی متغیر context را نمایش می‌دهند و به‌صورت پیش‌فرض escape می‌کنند.'), ('Use the context key.', 'کلید context را بنویس.'))
lesson('pro', 'django', 'blank', ('Define a model', 'تعریف مدل'),
       ('Choose the field class for a short title.', 'کلاس فیلد عنوان کوتاه را بنویس.'), 'from django.db import models\n\nclass Post(models.Model):\n    title = models.___(max_length=200)', ['CharField'],
       ('CharField stores short text with a maximum length.', 'فیلد CharField متن کوتاه را با طول حداکثر ذخیره می‌کند.'), ('This is a character field.', 'این فیلد برای نویسه‌هاست.'))
lesson('pro', 'django', 'order', ('Apply schema changes', 'اعمال تغییرات ساختار داده'),
       ('Arrange the workflow after changing a model.', 'روند پس از تغییر مدل را مرتب کن.'), '', [0, 1, 2],
       ('Edit the model, generate a migration, then apply it.', 'مدل را تغییر بده، فایل migration بساز و سپس آن را اعمال کن.'), ('Generate migrations before applying them.', 'migration را پیش از اعمال کردن بساز.'),
       ['# Edit models.py', 'python manage.py makemigrations', 'python manage.py migrate'])
lesson('pro', 'django', 'blank', ('Read published posts', 'خواندن نوشته‌های منتشرشده'),
       ('Complete the queryset method that selects matching rows.', 'متد انتخاب ردیف‌های مطابق شرط را کامل کن.'), 'posts = Post.objects.___(published=True)', ['filter'],
       ('filter returns a queryset containing rows matching the condition.', 'متد filter مجموعه‌ی ردیف‌های مطابق شرط را برمی‌گرداند.'), ('You may need multiple matching posts.', 'ممکن است چند نوشته مطابق شرط باشند.'))
lesson('pro', 'django', 'quiz', ('Protect a POST form', 'محافظت از فرم POST'),
       ('Which template tag belongs inside a POST form?', 'کدام تگ قالب باید داخل فرم POST قرار بگیرد؟'), '<form method="post">\n    <!-- tag here -->\n</form>', '{% csrf_token %}',
       ('The CSRF token helps Django reject forged state-changing requests.', 'توکن CSRF به جنگو برای رد درخواست‌های جعلیِ تغییر‌دهنده‌ی وضعیت کمک می‌کند.'), ('Look for the CSRF tag.', 'تگ CSRF را پیدا کن.'),
       ['{% csrf_token %}', '{{ password }}', '{% disable_security %}', '<csrf>'])
lesson('pro', 'django', 'blank', ('Validate a form', 'اعتبارسنجی فرم'),
       ('Complete the method before using cleaned_data.', 'متد را پیش از استفاده از cleaned_data کامل کن.'), 'form = PostForm(request.POST)\nif form.___():\n    title = form.cleaned_data["title"]', ['is_valid'],
       ('is_valid runs field and form validation before cleaned data is used.', 'متد is_valid پیش از استفاده از داده‌ها، فیلدها و فرم را اعتبارسنجی می‌کند.'), ('Validate before saving.', 'پیش از ذخیره، اعتبارسنجی کن.'))
lesson('pro', 'django', 'debug', ('Require authentication', 'الزام ورود'),
       ('Choose the decorator for a view that requires login.', 'دکوراتور ویویی را انتخاب کن که نیاز به ورود دارد.'), 'from django.contrib.auth.decorators import login_required\n\n# decorator here\ndef profile(request):\n    ...', '@login_required',
       ('login_required redirects anonymous users to the login page.', 'دکوراتور login_required کاربر مهمان را به صفحه‌ی ورود هدایت می‌کند.'), ('Use the imported decorator.', 'از دکوراتور واردشده استفاده کن.'),
       ['@login_required', '@public', '@staff_only', '@csrf_exempt'])
lesson('pro', 'django', 'quiz', ('A missing post', 'نوشته‌ی ناموجود'),
       ('Which helper returns 404 if the post is missing?', 'کدام تابع اگر نوشته وجود نداشته باشد، ۴۰۴ برمی‌گرداند؟'), '', 'get_object_or_404(Post, pk=post_id)',
       ('get_object_or_404 gets an object or raises Http404.', 'تابع get_object_or_404 شیء را پیدا می‌کند یا Http404 ایجاد می‌کند.'), ('Look for the 404 helper.', 'تابع کمکی ۴۰۴ را پیدا کن.'),
       ['get_object_or_404(Post, pk=post_id)', 'Post.objects.all()', 'print(post_id)', 'HttpResponse("missing")'])
lesson('pro', 'django', 'project', ('Mini project: blog page', 'پروژه‌ی کوچک: صفحه‌ی وبلاگ'),
       ('Complete the query and template shortcut.', 'خواندن داده‌ها و تابع قالب را کامل کن.'),
       'from django.shortcuts import render\nfrom .models import Post\n\ndef blog(request):\n    posts = Post.objects.___(published=True)\n    return ___(request, "blog.html", {"posts": posts})', [['filter'], ['render']],
       ('The view selects published posts and renders them using a template.', 'ویو نوشته‌های منتشرشده را انتخاب و با قالب نمایش می‌دهد.'),
       ('Filter the rows, then render the page.', 'ردیف‌ها را فیلتر کن و صفحه را نمایش بده.'))


BY_ID = {item['id']: item for item in LESSONS}


def public(item, detail=False):
    fields = ['id', 'track', 'topic', 'kind', 'title', 'xp']
    if detail:
        fields += ['prompt', 'code', 'hint', 'options']
    return {key: item[key] for key in fields if key in item}


def normalize(value):
    return str(value).strip().replace('\r\n', '\n')


def correct(item, submitted):
    if item['kind'] == 'order':
        return isinstance(submitted, list) and all(type(x) is int for x in submitted) and submitted == item['answer']
    if item['kind'] == 'project':
        return isinstance(submitted, list) and len(submitted) == len(item['answer']) and all(
            isinstance(value, str) and normalize(value) in accepted for value, accepted in zip(submitted, item['answer']))
    accepted = item['answer'] if isinstance(item['answer'], list) else [item['answer']]
    if not isinstance(submitted, str):
        return False
    return normalize(submitted) in accepted
