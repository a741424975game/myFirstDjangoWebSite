# -*- coding: UTF-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from lxml import etree
import urllib2
#from multiprocessing.dummy import Pool as ThreadPool
from django.contrib.auth.models import User
from Myapp.models import animation,animations_image,UserShared_animations,site
from django.contrib import auth
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# Create your views here.

def index(req):
    loginstatus=''
    if req.user.is_authenticated():
        loginstatus='active'
        username=req.user.username
    else:
        username=''
        loginstatus='not_active'
        
    content = {'loginstatus': loginstatus, 'username':username}
    return render_to_response('index.html', content, context_instance=RequestContext(req))

def animation_index(req):
    loginstatus=''
    if req.user.is_authenticated():
        loginstatus='active'
        username=req.user.username
        animations=(User.objects.get(username=req.user.username)).usershared_animations_set.all()
        if len(animations)>5:
            test_allow='true'
        else:
            test_allow='false'

        content = {'loginstatus': loginstatus, 'username':username,'animations':animations,'test_allow':test_allow,}
    else:
        test_allow='false'
        username=''
        loginstatus='not_active'
        content = {'loginstatus': loginstatus, 'username':username,'test_allow':test_allow,}
    return render_to_response('animation.html', content, context_instance=RequestContext(req))

def animation_shared(req):
    ret=''
    if req.POST:
        post=req.POST
        if post.get('animation_site',) and post.get('animation_url',) :
            url=post.get('animation_url',)
            site_name=post.get("animation_site",)
            if UserShared_animations.objects.filter(url=url):
                animation_url=UserShared_animations.objects.get(url=url)
                animation_url.username.add(req.user)
                if animation.objects.filter(url=url):
                    ret='success'
            else:
                user_animation_shared=UserShared_animations.objects.create(shared_type=(site.objects.get(site_name=site_name)),url=url)
                user_animation_shared.username.add(User.objects.get(username=req.user.username))
                user_animation_shared.save()
                req.user.usershared_animations_set.add(user_animation_shared)
                req.user.save()
                spider(site_name,req.user.username)
                if animation.objects.filter(url=url):
                    ret='success'
                else:
                    ret='fail'



    content={'sites':site.objects.all(),'return':ret}
    return render_to_response('shared_animation.html', content, context_instance=RequestContext(req))




        


def login(req):
    status = ''
    if req.POST:
        post=req.POST
        passwd=post.get('pd','')
        username=post.get('lusername','')
        user = auth.authenticate(username = username, password = passwd)
        if user is not None:
            if user.is_active:
                auth.login(req, user)
                status = 'active'
                return HttpResponseRedirect('/index',)

            else:
                status = 'not_active'
        else:
            status = 'not_exist_or_psswd_err'
    content = {'status': status,}
    return render_to_response('login.html', content, context_instance=RequestContext(req))

def register(req):
    status = ''
    if req.POST:
        post = req.POST
        passwd = post.get('pd', '')
        repasswd = post.get('pdc', '')
        if passwd != repasswd:
                status = 're_err'

        else:
            username = post.get('newusername', '')
            if User.objects.filter(username=username):
                status = 'user_exist'
            else:
                newuser = User.objects.create_user(username=username, password=passwd, email=post.get('email', ''))
                newuser.save()
                status = 'success'
    if status=='success':
        auth.login(req, auth.authenticate(username = username, password = passwd))
        return HttpResponseRedirect('/index')
    else:
        content = {'status': status,}
        return render_to_response('register.html', content, context_instance=RequestContext(req))
#登陆与注册同一页面模板使用user(req)
# def user(req):
#     status=''
#
#     if req.POST.get('newusername',):
#         if req.POST:
#             post = req.POST
#             passwd = post.get('pd', '')
#             repasswd = post.get('pdc', '')
#             if passwd != repasswd:
#                 status = 're_err'
#             else:
#                 username = post.get('newusername', '')
#                 if User.objects.filter(username=username):
#                     status = 'user_exist'
#                 else:
#                     newuser = User.objects.create_user(username=username, password=passwd, email=post.get('email', ''))
#                     newuser.save()
#                     status = 'success'
#     if req.POST.get('lusername',):
#         post=req.POST
#         passwd=post.get('pd','')
#         username=post.get('lusername','')
#         user = auth.authenticate(username = username, password = passwd)
#
#         if user is not None:
#             if user.is_active:
#                 auth.login(req, user)
#                 status = 'active'
#                 return HttpResponseRedirect('/index',)
#
#             else:
#                 status = 'not_active'
#         else:
#             status = 'not_exist_or_psswd_err'
#     content = { 'status': status, 'user': ''}
#     return render_to_response('user.html', content, context_instance=RequestContext(req))
#
def logout(req):
    auth.logout(req)
    return HttpResponseRedirect('/index',)

# (将models数据换成字典)多余!!!
# def get_animations_infos(username):
#     user=User.objects.get(username=username)
#     user_shared_animations=user.usershared_animations_set.all()
#     animations={}
#     animation_infos={'url':'','image_id':'','title':'','tag':'','info':'','time':''}
#     for i in range(len(user_shared_animations)):
#         animation=user_shared_animations[i].animation
#         animation_infos['image_id']=animation.animations_image.image_id
#         animation_infos['url']=animation.url
#         animation_infos['title']=animation.title
#         animation_infos['tag']=animation.tag
#         animation_infos['info']=animation.info
#         animation_infos['time']=animation.time
#         animations[i]=animation_infos
#     return (animations)
def spider(site_type,username):
    if site_type=='acfun' :
        acfunspider(username)

def acfunspider(username):
    acfunurl="http://www.acfun.tv/"
    user_shared_animations=(User.objects.get(username=username)).usershared_animations_set.all()
    for url in user_shared_animations:
        urlt=url.url
        for i in range(len(acfunurl)):
            if urlt[i]!=acfunurl[i]:
                UserShared_animations.objects.filter(url=urlt).delete()
                break
            else:
                continue
        if UserShared_animations.objects.filter(url=urlt):
            if animation.objects.filter(url=urlt):
                url.username.add(User.objects.get(username=username))
                continue
            else:
                html=requests.get(urlt)
                selector = etree.HTML(html.text)
                if selector.xpath('//*[@id="block-data-view"]/@data-tags'):
                    title=''.join((selector.xpath('//*[@id="txt-title-view"]/text()')))
                    type = ''.join(selector.xpath('//*[@id="area-title-view"]/p/a[2]/text()'))
                    time = ''.join(selector.xpath('//*[@id="area-title-view"]/div[1]/p/span[2]/text()'))
                    if  selector.xpath('//*[@id="block-info-view"]/div/p/text()'):
                        info= ''.join(selector.xpath('//*[@id="block-info-view"]/div/p/text()')[0])
                    else:
                        info=''
                    tag  = ''.join(selector.xpath('//*[@id="block-data-view"]/@data-tags'))
                    image_url = ''.join(selector.xpath('//*[@id="block-data-view"]/@data-preview'))
                    if title:
                        ansh = animation.objects.create(animation_url=url,url=url.url,title=title,type=type,time=time,info=info,tag=tag,image_url=image_url,)
                        ansh.save()
                        acimage_id=''
                        strurl=str(url.url)
                        for i in range(22,len(strurl)):
                            acimage_id+=strurl[i]
                        if title:
                            ai = animations_image.objects.create(image_url=ansh,image_id=acimage_id)
                            ai.save()
                        if  image_url:
                            dlimage(image_url,acimage_id)

                    else:
                        UserShared_animations.objects.filter(url=urlt).delete()




                else:
                    title=''.join((selector.xpath('//*[@id="block-data-view"]/@data-title')))
                    type = ''.join(selector.xpath('//*[@id="area-title-view"]/div[1]/p/a[2]/text()'))
                    time = ''.join(selector.xpath('//*[@id="date-title"]/text()'))
                    info= ''.join(selector.xpath('//*[@id="block-data-view"]/@data-desc'))
                    tag  = ''
                    image_url = ''.join(selector.xpath('//*[@id="block-data-view"]/@data-cover'))
                    if title:
                        ansh = animation.objects.create(animation_url=url,url=url.url,title=title,type=type,time=time,info=info,tag=tag,image_url=image_url,)
                        ansh.save()
                        acimage_id=''
                        strurl=str(url.url)
                        for i in range(22,len(strurl)):
                            acimage_id+=strurl[i]
                        ai = animations_image.objects.create(image_url=ansh,image_id=acimage_id)
                        ai.save()
                        if  image_url:
                            dlimage(image_url,acimage_id)
                    else:
                        UserShared_animations.objects.filter(url=urlt).delete()
        else:
            continue



#b站爬虫因网页乱码暂时不可用(未添加SharedType)
# def bilibilispider(username):
#     user_shared_animations=(User.objects.get(username=username)).usershared_animations_set.all()
#     for url in user_shared_animations:
#         urlt=url.url
#         if animation.objects.filter(url=urlt):
#             continue
#         else:
#             html=requests.get(urlt)
#             selector = etree.HTML(html.text)
#             title = selector.xpath('/html/body/div[4]/div[1]/div[2]/div[1]/div[1]/h1/text()')
#             type = selector.xpath('/html/body/div[4]/div[1]/div[2]/div[1]/div[3]/span[2]/a/text()')
#             time = selector.xpath('/html/body/div[4]/div[1]/div[2]/div[1]/div[3]/time/i/text()')
#             info  = selector.xpath('/html/body/div[4]/div[3]/div[3]/div[1]/div[2]/text()')
#             tag  = selector.xpath('/html/body/div[4]/div[3]/div[3]/div[1]/div[1]/ul/li/a/@title')
#             image_url = selector.xpath('//*[@id="comprehensive-sp"]/div/div/ul/li[1]/a/div/img/@src')#未获取
#             play = selector.xpath('//*[@id="comprehensive-sp"]/div/div/ul/li[1]/div/div[1]/i[2]/text()')#未获取
#             danmu  = selector.xpath('//*[@id="comprehensive-sp"]/div/div/ul/li[1]/div/div[1]/i[4]/text()')  #未获取
#             collect = selector.xpath('//*[@id="comprehensive-sp"]/div/div/ul/li[1]/div/div[1]/i[5]/text()') #未获取
#             ansh = animation.objects.create(animation_url=url,url=url.shared,title=title,type=type,time=time,info=info,tag=tag,image_url=image_url,)
#             ansh.save()
def dlimage(url, imagename):
        localSavePath = 'Mysite/static/images/'
        imgName = localSavePath + "%s.jpg" % imagename
        urllib.urlretrieve(url, imgName)

def animation_shared_host(req,name):
    if req.user.is_authenticated():
        loginstatus='active'
    else:
        loginstatus='not_active'
    if User.objects.filter(username=name):
        animations=(User.objects.get(username=name)).usershared_animations_set.all()
        content = {'loginstatus': loginstatus, 'username':req.user.username,'animations':animations,}
        return render_to_response('animation.html', content, context_instance=RequestContext(req))
    else:
        return render_to_response('404.html')













            


    




