"""
Django settings for splat project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import  time
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#2etqz-s!5^z_1z=^k&!#2an_b=a$@7(d@x6)$51r&y+=_%#-h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'web',
    'django_apscheduler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = 'splat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'splat.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'splat',
        'USER': 'splat',
        'PASSWORD': 'Abc.123!@#',
        'HOST': '172.30.10.131',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (os.path.join(BASE_DIR,  'templates'),)

#STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, "static"),
# ]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
#STATIC_ROOT = 'static'
#Simple setting

#服务器信息
SIMPLEUI_HOME_INFO = False
#快速操作
SIMPLEUI_HOME_QUICK = False
#最近动作
SIMPLEUI_HOME_ACTION = False
#Simple 使用分析
SIMPLEUI_ANALYSIS = False
SIMPLEUI_LOADING = False

#菜单设置
SIMPLEUI_CONFIG = {
    'system_keep': True,
    'menu_display': ['服务器扫描','黑白名单','多级菜单测试', '权限认证', '动态菜单测试'],      # 开启排序和过滤功能, 不填此字段为默认排序和全部显示, 空列表[] 为全部不显示.
    'dynamic': True,    # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容
    'menus': [{
        'name': 'Simpleui',
        'icon': 'fas fa-code',
        'url': 'https://gitee.com/tompeppa/simpleui'
    }, {
        'app': 'auth',
        'name': '权限认证',
        'icon': 'fas fa-user-shield',
        'models': [{
            'name': '用户',
            'icon': 'fa fa-user',
            'url': 'auth/user/'
        }]
    }, {
        'name': '服务器扫描',
        'icon': 'far fa-surprise',
        'models': [{
            'name': '客户端列表',
            'icon': 'fa fa-user',
            'url': 'web/active_ip'
        },{
            'name': '进程扫描列表',
            'url': 'web/idcscan',
            'icon': 'fab fa-github'
        },{
            'name': '网络连接检测',
            'url': 'web/outgonging_detection',
            'icon': 'fab fa-github'
        },{
            'name': '文件完整性',
            'url': 'web/project_info',
            'icon': 'fab fa-github'
        },{
            'name': '异常文件信息',
            'url': 'web/change_file',
            'icon': 'fab fa-github'
        },{
            'name': '定时任务',
            'url': 'web/cron_info',
            'icon': 'fab fa-github'
        },{
            'name': '外网连接',
            'url': 'web/expnetwork_info',
            'icon': 'fab fa-github'
        }]
    },{
        'name': '黑白名单',
        'icon': 'far fa-surprise',
        'models': [{
            'name': '进程白名单',
            'icon': 'fa fa-user',
            'url': 'web/process_whitelist'
        },{
            'name': 'ip黑名单',
            'icon': 'fab fa-github',
            'url': 'web/ipaddress_blacklist'
        }]
    },{
        # 自2021.02.01+ 支持多级菜单，models 为子菜单名
        'name': '多级菜单测试',
        'icon': 'fa fa-file',
      	# 二级菜单
        'models': [{
            'name': 'Baidu',
            'icon': 'far fa-surprise',
            # 第三级菜单 ，
            'models': [
                {
                  'name': '爱奇艺',
                  'url': 'https://www.iqiyi.com/dianshiju/'
                  # 第四级就不支持了，element只支持了3级
                }, {
                    'name': '百度问答',
                    'icon': 'far fa-surprise',
                    'url': 'https://zhidao.baidu.com/'
                }
            ]
        }, {
            'name': '内网穿透',
            'url': 'web/idcscan',
            'icon': 'fab fa-github'
        }]
    }, {
        'name': '动态菜单测试' ,
        'icon': 'fa fa-desktop',
        'models': [{
            'name': time.time(),
            'url': 'http://baidu.com',
            'icon': 'far fa-surprise'
        }]
    }]
}

#首页页面设置
# SIMPLEUI_HOME_PAGE = '/dashboard'
SIMPLEUI_HOME_PAGE = '/index'
SIMPLEUI_HOME_TITLE = '首页'
SIMPLEUI_HOME_ICON = 'fa fa-eye'