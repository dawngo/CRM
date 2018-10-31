from app01.models import *
from stark.service.sites import site, ModelStark
from django.utils.safestring import mark_safe
from django.shortcuts import redirect, render, HttpResponse
from django.conf.urls import url
from django.http import JsonResponse


class SchoolConfig(ModelStark):
    list_display = ['title']


site.register(School, SchoolConfig)


class DepartmentConfig(ModelStark):
    list_display = ['title', 'code']


site.register(Department, DepartmentConfig)


class UserInfoConfig(ModelStark):
    def display_gender(self, obj=None, is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()

    list_display = ['name', display_gender, 'depart', 'user']


site.register(UserInfo, UserInfoConfig)
site.register(Course)


class ClassConfig(ModelStark):
    list_display = ["course", "semester", "teachers", "tutor"]


site.register(ClassList, ClassConfig)


class CustomerConfig(ModelStark):
    def display_gender(self, obj=None, is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()

    def display_course(self, obj=None, is_header=False):
        if is_header:
            return "咨询课程"

        link_list = []
        for course in obj.course.all():
            s = "<a>%s</a>" % course.name
            link_list.append(s)

        return mark_safe("  ".join(link_list))

    list_display = ["name", display_gender, "consultant", display_course]


site.register(Customer, CustomerConfig)
site.register(ConsultRecord)


class StudentConfig(ModelStark):
    def student_info(self, request, sid):
        if request.is_ajax():
            cid = request.POST.get('cid')
            # 查询学生sid在班级cid下的所有成绩
            student_study_record_list = StudentStudyRecord.objects.filter(student=sid, classstudyrecord__class_obj=cid)

            ret = [['day{}'.format(student_study_record.classstudyrecord.day_num), student_study_record.score] for
                   student_study_record in student_study_record_list]
            return JsonResponse(ret, safe=False)

        student_obj = Student.objects.filter(pk=sid).first()
        class_list = student_obj.class_list.all()
        return render(request, 'student_info.html', locals())

    def extra_url(self):
        temp = []
        temp.append(url('(\d+)/info/', self.student_info))
        return temp

    def display_score(self, obj=None, is_header=False):
        if is_header:
            return '详细信息'
        return mark_safe("<a href='/stark/app01/student/{}/info/'>详细信息</a>".format(obj.pk))

    list_display = ['customer', 'class_list', display_score]


site.register(Student, StudentConfig)


class ClassStudyRecordConfig(ModelStark):
    def record_score(self, request, cls_record_id):
        if request.is_ajax():
            action = request.POST.get('action')
            sid = request.POST.get('sid')
            val = request.POST.get('val')
            StudentStudyRecord.objects.filter(pk=sid).update(**{action: val})
            return HttpResponse('ok')

        if request.method == 'POST':
            print(request.POST)
            dic = {}
            for key, value in request.POST.items():
                if key == 'csrfmiddlewaretoken':
                    continue
                field, pk = key.rsplit('_', 1)

                if pk in dic:
                    dic[pk][field] = value
                else:
                    dic[pk] = {field: value}

            for pk, update_data in dic.items():
                StudentStudyRecord.objects.filter(pk=pk).update(**update_data)

            return redirect(request.path)

        # 班级学习记录对象
        cls_record = ClassStudyRecord.objects.get(pk=cls_record_id)
        # 该班级的学习记录对象关联的所有的学生学习记录对象
        student_study_record_list = cls_record.studentstudyrecord_set.all()
        # 成绩选项
        score_choices = StudentStudyRecord.score_choices
        return render(request, 'record_score.html', locals())

    def extra_url(self):
        temp = []
        temp.append(url("(\d+)/record_score/", self.record_score))
        return temp

    def display_info(self, obj=None, is_header=False):
        if is_header:
            return "详细信息"
        return mark_safe("<a href='/stark/app01/studentstudyrecord/?classstudyrecord=%s'>详细信息</a>" % obj.pk)

    def handle_score(self, obj=None, is_header=False):
        if is_header:
            return '录入成绩'
        return mark_safe("<a href='/stark/app01/classstudyrecord/{}/record_score/'>录入成绩</a>".format(obj.pk))

    list_display = ["class_obj", "day_num", "teacher", "homework_title", display_info, handle_score]

    def patch_init(self, queryset):

        for cls_study_obj in queryset:

            # 查询班级关联的所有的学生
            student_list = cls_study_obj.class_obj.student_set.all()
            ssr_list = []
            for student in student_list:
                ssr = StudentStudyRecord(student=student, classstudyrecord=cls_study_obj)
                ssr_list.append(ssr)

            StudentStudyRecord.objects.bulk_create(ssr_list)

    patch_init.desc = "创建关联学生学习记录"

    actions = [patch_init]


site.register(ClassStudyRecord, ClassStudyRecordConfig)


class StudentStudyRecordConfig(ModelStark):

    def edit_record(self, request, id):
        record = request.POST.get("record")
        StudentStudyRecord.objects.filter(pk=id).update(record=record)
        return HttpResponse("OKOKOK")

    def extra_url(self):
        temp = []
        temp.append(url(r"(\d+)/edit_record/$", self.edit_record), )
        return temp

    def display_record(self, obj=None, is_header=False):
        if is_header:
            return "出勤"

        html = "<select name='record' class='record' pk=%s>" % obj.pk
        for item in StudentStudyRecord.record_choices:

            if obj.record == item[0]:
                option = "<option selected value='%s'>%s</option>" % (item[0], item[1])
            else:
                option = "<option value='%s'>%s</option>" % (item[0], item[1])

            html += option
        html += "</select>"
        return mark_safe(html)

    def display_score(self, obj=None, is_header=False):
        if is_header:
            return "成绩"
        return obj.get_score_display()

    list_display = ["student", "classstudyrecord", display_record, display_score]

    def patch_late(self, queryset):
        queryset.update(record="late")

    patch_late.desc = "迟到"
    actions = [patch_late]


site.register(StudentStudyRecord, StudentStudyRecordConfig)
