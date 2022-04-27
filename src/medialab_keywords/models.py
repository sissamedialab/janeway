from django.db import models

# Create your models here.
class KeywordGroup(models.Model):
    groupId = models.CharField(max_length=5);
    groupName = models.CharField(max_length=200)

    def __str__(self):
        return '%s %s' % (self.groupId, self.groupName)

    
class KeywordSubgroup(models.Model):
    subgroupId = models.CharField(max_length=5);        
    subgroupName = models.CharField(max_length=200)
    kgroup=models.ForeignKey(KeywordGroup, on_delete=models.CASCADE)

    def __str__(self):
        return '%s %s' % (self.subgroupId, self.subgroupName)

    
class Keyword(models.Model):
    keywordId = models.CharField(max_length=5)
    keywordName = models.CharField(max_length=200)
    ksubgroup = models.ForeignKey(KeywordSubgroup, on_delete=models.CASCADE)

    def __str__(self):
        return '%s %s' % (self.keywordId, self.keywordName)
