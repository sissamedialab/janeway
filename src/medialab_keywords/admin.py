from django.contrib import admin

# Register your models here.
from medialab_keywords import models

class KeywordGroupAdmin(admin.ModelAdmin):
    list_display = ('groupId', 'groupName');
    
class KeywordSubgroupAdmin(admin.ModelAdmin):
    list_display = ('subgroupId', 'subgroupName')

class KeywordAdmin(admin.ModelAdmin):
    list_display = ('keywordId', 'keywordName')

admin_list = [
    (models.KeywordGroup, KeywordGroupAdmin),
    (models.KeywordSubgroup, KeywordSubgroupAdmin),
    (models.Keyword, KeywordAdmin),
 
]
    
[admin.site.register(*t) for t in admin_list]

