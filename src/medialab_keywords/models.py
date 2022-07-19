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

class Role(models.Model):
    roleId = models.CharField(max_length=10)
    name = models.CharField(max_length=50)

class User(models.Model):
    userId = models.CharField(max_length=200)
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    editorWorkload = models.IntegerField()
    
    roles=models.ManyToManyField(Role, through='User_Role')

    def __str__(self):
        return "userCod:" + str(self.id) + "; " + \
            "userId: " + \
            self.userId + "(" + self.firstName + ", " + self.lastName + "); " + \
            "maxworkload: " + str(self.editorWorkload)

    # def set_this_month_workload(self, v):
    #     self.this_month_workload = v

    # def get_this_month_workload(self):
    #     return self.this_month_workload
    
class User_Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    disableFlag=models.IntegerField()


class Editor_Keyword(models.Model):
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    weight = models.IntegerField()


class Document(models.Model):
    preprintid = models.CharField(max_length=200)


class Version(models.Model):
    version_number = models.IntegerField();
    document = models.ForeignKey(Document, on_delete=models.CASCADE)


class Action_History(models.Model):
    actionCod = models.IntegerField()
    agentCod = models.ForeignKey(User, null=True, related_name='actor') # The user who acted
    userCod = models.ForeignKey(User, null=True, related_name='receiver') # The user to whom is sent
    realAgentCod = models.ForeignKey(User, null=True, related_name='real_actor') # the impersonating user;
    actionDate = models.DateTimeField() # The action Date
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
