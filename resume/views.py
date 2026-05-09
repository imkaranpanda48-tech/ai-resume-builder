from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from .utils import parse_resume, calculate_ats
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse

# upload resume 
def upload_resume(request):
    if request.method == "POST":
        resume_file = request.FILES.get("resume")

        if not resume_file:
            return render(request, "resume/upload.html", {"error": "Please upload a resume"})

        data = parse_resume(resume_file)
        ats = calculate_ats(data)

        # store data in session for next steps
        request.session["data"] = data
        request.session["ats"] = ats

        return redirect("ats_score")

    return render(request, "resume/upload.html")


# edit resume 
def edit(request):
    data = request.session.get("data", {})

    if request.method == "POST":
        for field in data:
            if field in request.POST:
                value = request.POST.get(field).strip()

                if field in ["skill", "Education", "Past Work Experience"]:
                    data[field] = [s.strip() for s in value.splitlines() if s.strip()]
                else:
                    data[field] = value

        # experience fields
        data["exp_job_title"] = request.POST.get("exp_job_title", "")
        data["exp_company"] = request.POST.get("exp_company", "")
        data["exp_start"] = request.POST.get("exp_start", "")
        data["exp_end"] = request.POST.get("exp_end", "")
        data["exp_years"] = request.POST.get("exp_years", "")
        data["exp_description"] = request.POST.get("exp_description", "")

        request.session["data"] = data
        return redirect("choose_template")

    return render(request, "resume/edit.html", {"data": data})



#choose templates classic, modern, proffesional 
def choose_template(request):
    data = request.session.get("data")

    if not data:
        return redirect("upload_resume")

    return render(request, "resume/choose_template.html", {"data": data})


# genrate pdf 
def generate_pdf(request, template):
    data = request.session.get('data')

    if not data:
        return HttpResponse("No resume data found")

    template_path = f"resume/resume_{template}.html"
    template = get_template(template_path)

    html = template.render({"data": data})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("PDF generation error")

    return response


# Ats Score 
def ats_score(request):
    ats = request.session.get("ats")
    return render(request, "resume/ats_score.html", {"ats": ats})


