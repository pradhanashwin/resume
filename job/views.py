from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from job.forms import JobForm, JobModelForm, ParsedResumeForm, FacetedProductSearchForm 
from job.models import Job, Field, Applicant, TempResume, ParsedResume
from accounts.models import Company, Address
from job.resume_verifier import Resume 
from haystack.query import SearchQuerySet
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView


# This function is for the authorization
def job_poster(user):
    return user.groups.filter(name='company').exists()


def load_home(request):
    parsedvalue = []

    if request.method == 'POST':
        resume = request.FILES['temp_resume']
        data = resume.read()
        print(data)

        resume_status1 = Resume.resume_verifier(data)
        resume_status = Resume.resume_classifier(data)
            
        if resume_status:
            user = request.user
            
            temp = TempResume.objects.create(temp_resume=resume)

            if user.is_authenticated:
                user.recent_resume = temp.temp_resume
                user.save()
            messages.success(request, 'Resume Uploaded Successfully!')

            scraped_dict = Resume.parse_resume()

            print(scraped_dict)

            parsedvalue = ParsedResume.objects.create(
                                        applied_for=scraped_dict['applied_for'],
                                        personal_info=scraped_dict['personal_info'], 
                                        education=scraped_dict['education'], 
                                        experience=scraped_dict['experience'],
                                        skills=scraped_dict['skills'])
            if user.is_authenticated:
                # Add other fields as per the model
                try:
                
                    UserProfile.objects.create(user=request.user)

                except:
                    messages.error(request, ' ')

        else:
            messages.error(request, 'The Resume is not valid, try again!')

    companies = Company.objects.all()
    jobs = []
    for company in companies:
        j = Job.objects.filter(company=company).order_by('-id')[:2]
        print(j)
        if len(j) > 0:
            jobs.append(j)
    try:
        featured_job = Job.objects.all()[0]
    except Exception as e:
        print(e)
        featured_job = []
    fields = Field.objects.all()[:5]
    context_dict = {'jobs': jobs, 'fields': fields, 'featured_job': featured_job, 'parsedvalue': parsedvalue}

    return render(request, 'home.html', context_dict)


def post_job(request):
    if request.method == 'POST':
        form = JobModelForm(request.POST)
        if form.is_valid():
            company = Company.objects.get(user=request.user)
            job = form.save(commit=False)
            job.company = company
            form.save()
            messages.success(request, 'Job Posted Successfully!')
        else:
            messages.error(request, 'Something is Wrong, try again!')
    else:
        form = JobForm(None)
        # To display different options for job field
    fields = Field.objects.all()
    context_dict = {'form': form, 'fields': fields}
    return render(request, 'job/postjob.html', context_dict)


def job_detail(request, slug):
    job = Job.objects.get(slug=slug)
    if request.method == 'POST' and request.FILES['resume']: 
        user = request.user
        resume = request.FILES['resume']
        
        # Uses machine learning to verify the resume
        resume_status = Resume.resume_verifier()

        if resume_status is True:
            # print (job)
            # if User applies again to update their credentials
            if Applicant.objects.filter(job=job, applicant=user):
                applicant = Applicant.objects.get(job=job, applicant=user)
                applicant.delete()
                Applicant.objects.create(name= request.POST.get('name'), email=request.POST.get('email'), job=job,
                                         applicant=user, resume=resume)
                messages.success(request, 'Reapplied with updated credentials')
            
            # Appling for the first time
            else:
                Applicant.objects.create(name= request.POST.get('name'), email=request.POST.get('email'), job=job,
                                         applicant=user, resume=resume)
                messages.success(request, 'Job applied Successfully!')

        else:
            messages.error(request, 'Invalid resume')

    related_jobs = Job.objects.filter(job_field= job.job_field).exclude(slug=slug)
    context_dict = {'job': job, 'related_jobs': related_jobs}
    return render(request, 'job/job-detail.html', context_dict)


def view_by_field(request, id):
    field = Field.objects.get(id=id)
    jobs = Job.objects.filter(job_field=field)
    return render(request, 'job/by-field.html', {'jobs': jobs})


def edit_job(request, slug):
    if request.method == 'POST':
        job = Job.objects.get(slug=slug)
        form = JobModelForm(request.POST, instance=job)
        company = Company.objects.get(user=request.user)
        if form.is_valid():

            form.save()
            messages.success(request, 'Job Posting Edited!')
        else:
            messages.error(request, 'Something is Wrong, try again!')
        return HttpResponseRedirect('/')
    else:
        form = JobForm()
        job = Job.objects.get(slug=slug)
        # To display different options for job field
        fields = Field.objects.all()
        context_dict = {'form': form, 'fields': fields, 'job': job}
        return render(request, 'job/edit-job.html', context_dict)


def see_applicants(request, slug):
    job = Job.objects.get(slug=slug)
    applicants = Applicant.objects.filter(job=job)
    # job sent for displaying job title

    return render(request, 'job/view-applicants.html', {'applicants': applicants, 'job': job})


def edit_parsed_data(request):
    parsedvalue = ParsedResume.objects.all().order_by('-id')[0]
    
    if request.method == 'POST':
        form = ParsedResumeForm(request.POST, instance=parsedvalue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Edited Successfully!')
        else:
            messages.error(request, 'Something is Wrong, try again!')
        return HttpResponseRedirect('/')
    else:
        form = ParsedResumeForm()
        context_dict = {'form': form, 'parsedvalue': parsedvalue}
        return render(request, 'edit_parsed_detail.html', context_dict)


def filtered_job(request):
    job = []
    ids = Resume.filtered_jobs()
    for i in ids:
        try:
            job.append(Job.objects.get(id=i))
        
        except:

            pass

    context_dict = {'jobs': job}
    return render(request, 'filtered_jobs.html', context_dict)


def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(
        content_auto=request.GET.get(
            'q',
            ''))[:5]
    s = []
    for result in sqs:
        d = {"value": result.title, "data": result.object.slug}
        s.append(d)
    output = {'results': s}
    return JsonResponse(output)


class FacetedSearchView(BaseFacetedSearchView):

    form_class = FacetedProductSearchForm
    facet_fields = ['type_of_job', 'industry', 'contract_type', 'level_of_job', 'experience']
    template_name = 'search_result.html'
    paginate_by = 3
    context_object_name = 'object_list'
