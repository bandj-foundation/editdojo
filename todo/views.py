import requests
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import TodoItem, ClassifiedImage


# Create your views here.
def todoView(request):
    all_todo_items = TodoItem.objects.all()
    return render(request,'todo.html',
        {'all_items': all_todo_items})

def addTodo(request):
    c=request.POST['content']
    new_item = TodoItem(content=c)
    new_item.save()
    return HttpResponseRedirect('/todo/')

def deleteTodo(request, todo_id):
    item_to_delete= TodoItem.objects.get(id=todo_id)
    item_to_delete.delete()
    return HttpResponseRedirect('/todo/')

def classifyImage(request):
    image_url=request.POST['url']
    # get ratings from model hosted on nanonets
    url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelUrls/'
    
    headers = {
    'accept': 'application/x-www-form-urlencoded'
    }

    image_url_list=[]
    image_url_list.append(image_url)
    
    data = {
        'modelId': 'e483f029-8ad6-43c4-a0ca-1377a2d04078',
        'urls' : image_url_list
    }
    
    response = requests.request('POST', url, headers=headers, auth=requests.auth.HTTPBasicAuth('4S_Y0S2gS0DSpnZlz7fwPDa5W5oP5zuA', ''), data=data)

    ratings = response.text
    
    labels = ["\"Minimalism\"", "\"Cubism\"", "\"Romanticism\"", "\"Rococo\"", "\"Early_Renaissance\"", "\"Post_Impressionism\"", "\"Ukiyo_e\"", "\"Symbolism\"", "\"Pointillism\"", "\"Art_Noveau_Modern\"", "\"Contemporary_Realism\"", "\"Northern_Renaissance\"", "\"Expressionism\"", "\"Mannerism_Late_Renaissance\"", "\"Baroque\"", "\"Action_painting\"", "\"Pop_Art\"", "\"Analytical_Cubism\"", "\"Fauvism\"", "\"Color_Field_Painting\"", "\"Synthetic_Cubism\"", "\"Realism\"", "\"Native_Art_Primitivism\"", "\"New_Realism\"", "\"Impressionism\"", "\"High_Renaissance\"", "\"Abstract_Expressionism\""]
    eras = ["Minimalism", "Cubism", "Romanticism", "Rococo", "Early Renaissance", "Post Impressionism", "Ukiyo-e", "Symbolism", "Pointillism", "Art Noveau (Modern)", "Contemporary Realism", "Northern Renaissance", "Expressionism", "Mannerism (Late Renaissance)", "Baroque", "Action Painting", "Pop Art", "Analytical Cubism", "Fauvism", "Color Field Painting", "Synthetic Cubism", "Realism", "Naïve Art (Primitivism)", "New Realism", "Impressionism", "High Renaissance", "Abstract Expressionism"]
    probabilities = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    # loop through string from nanonets
    for i in range(27):
        try:
            era = labels[i]
            probabilities[i] = float(ratings[ratings.index(":", ratings.index(era)) + 1 : ratings.index("}", ratings.index(era))])
            print ("%s: %.3f%%" % (eras[i], probabilities[i] * 100))
        except ValueError:    
            None

    # get highest probability era        
    era1Label = eras[probabilities.index(max(probabilities))]
    era1Probability = max(probabilities)
    print ("\nPrimary era similarity is: %s, %.3f%%" % (era1Label, era1Probability * 100))

    # remove maximum to get second
    eras.remove(era1Label)
    probabilities.remove(era1Probability)

    # get second highest probability era
    era2Label = eras[probabilities.index(max(probabilities))]
    era2Probability = max(probabilities)
    print ("Secondary era similarity is: %s, %.3f%%" % (era2Label, era2Probability * 100))

    ret="Secondary era similarity is:" + str(era2Label) + " " + str(era2Probability * 100) + "%"
    cimg= ClassifiedImage()
    cimg.img = image_url
    cimg.label=ret
    return render(request, "todo.html", {'cimg':cimg})
 
