# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from inspect import getmembers
from .models import KeywordGroup
from .models import KeywordSubgroup
from .models import Keyword
from .models import User
from .models import Role
from .models import User_Role
from .models import Action_History
from .models import Editor_Keyword
from .models import Document
from .models import Version

from .eas import assign_editor, getDocument1, getDocument2, getDocument3, XDocument

import mysql.connector
from mysql.connector import Error

# Create your views here.
def index(request):
    return HttpResponse("Hello, keywords index.")

def groupdetail(request, group_id):
    return HttpResponse("You're looking at group %s." % group_id)

def subgroupdetail(request, subgroup_id):
    response = "You're looking at subgroup %s."
    return HttpResponse(response % subgroup_id)

def keyworddetail(request, keyword_id):
    return HttpResponse("You're looking at keyword %s." % keyword_id)

def keywords_list(request):
    metadata = "User metadata"
    kg = KeywordGroup.objects.all()
    context = { 'keyword_groups' : kg }
    return render(request, 'medialab_keywords/keywords_list.html', context )

def keywords_management(request):
    context={ }
    return render(request, 'medialab_keywords/keywords_management.html', context )

def load_keywords(request):
    # connect to the database
    try:
        c = mysql.connector.connect(host="kisman.ud.sissamedialab.it", database="wjJhepDb", user="c.zoicas-ro", password="SSSS123X", buffered=True)
        
        if c.is_connected():

            KeywordGroup.objects.all().delete()
            KeywordSubgroup.objects.all().delete()
            Keyword.objects.all().delete()
            User.objects.all().delete()
            Role.objects.all().delete()
            User_Role.objects.all().delete()
            Editor_Keyword.objects.all().delete()
            Version.objects.all().delete()
            Document.objects.all().delete()
            Action_History.objects.all().delete()

            # db_Info = c.get_server_info()
            # print("Connected to MySQL Server version ", db_Info)
            crsrKGroup = c.cursor()
            crsrKSubgroup = c.cursor()
            crsrKeyword = c.cursor()
            crsrUser = c.cursor()
            crsrUserRole = c.cursor()
            crsrRole = c.cursor()
            crsrActHist = c.cursor();
            crsrEditorKeywords = c.cursor()
            crsrDocument = c.cursor()
            crsrVersion = c.cursor()
            
            q_select_kgroup = ("SELECT groupCod, groupID, groupName FROM KGroup");
            q_select_ksubgroup = ("SELECT subgroupCod, subgroupID, subgroupName, groupCod FROM KSubgroup");
            q_select_keyword = ("SELECT Keyword.keywordCod, keywordID, keywordName, subgroupCod FROM Keyword INNER JOIN Keyword_KSubgroup ON Keyword.keywordCod = Keyword_KSubgroup.keywordCod");
            q_select_user = ("SELECT User.userCod, userId, firstName, lastName, editorWorkload FROM User");
            q_select_user_role = ("SELECT User_Role.userCod, User_Role.roleCod, User_Role.disableFlag FROM User INNER JOIN User_Role ON User.userCod = User_Role.userCod");
            q_select_role = ("SELECT roleCod, roleId, name FROM Role");
            q_select_edt_kwd = ("SELECT editorCod, keywordCod, keywordWeight FROM Editor_Keyword")
            q_select_document = ("SELECT documentCod, prePrintId FROM Document")
            q_select_version = ("SELECT versionCod, versionNumber, documentCod FROM Version")
            q_select_act_hist = ("SELECT actHistCod, versionCod, actionCod, agentCod, userCod, realAgentCod, actionDate FROM Action_History INNER JOIN Version USING(versionCod) WHERE YEAR(actionDate) >= 2022 and Version.submissionDate <= 20220627080000")

            crsrKGroup.execute( q_select_kgroup )
            crsrKSubgroup.execute( q_select_ksubgroup )
            crsrKeyword.execute( q_select_keyword )
            crsrUser.execute( q_select_user )
            crsrUserRole.execute( q_select_user_role )
            crsrRole.execute( q_select_role )
            crsrEditorKeywords.execute(q_select_edt_kwd)
            crsrDocument.execute(q_select_document)
            crsrVersion.execute(q_select_version)
            
            crsrActHist.execute(q_select_act_hist)
            number_of_rows=crsrActHist.rowcount
            
            for (groupCod, groupID, gName) in crsrKGroup:
                kg = KeywordGroup(id=groupCod, groupId=groupID, groupName=gName)
                kg.save();
                # print("{}, {}, {}".format(groupCod, groupID, gName))
                 
            print( "---- doen kgroup ----------------------------------------");
            
            for (subgroupCod, subgroupID, subgroupName, groupCod) in crsrKSubgroup:
                ksg = KeywordSubgroup(id=subgroupCod, subgroupId=subgroupID, subgroupName=subgroupName, kgroup_id=groupCod)
                ksg.save()
                # print("{}, {}, {}".format(subgroupCod, subgroupID, subgroupName))
                
            print( "---- done ksubgroup ----------------------------------------");
            
            for (keywordCod, keywordID, keywordName, subgroupCod) in crsrKeyword:
                kwd = Keyword(id = keywordCod, keywordId = keywordID, keywordName = keywordName, ksubgroup_id=subgroupCod)
                kwd.save()
                # print("{}, {}, {}, {}".format(keywordCod, keywordID, keywordName, subgroupCod))
                
            print( "---- done keyword --------------------------------------------");


            print( "---- start loading user --------------------------------------------");
            for (userCod, userId, firstName, lastName, editorWorkload) in crsrUser:
                user = User(id = userCod, userId = userId, firstName = firstName, lastName = lastName, editorWorkload = editorWorkload )
                user.save()
                # print("{}, {}, {}, {}, {}".format(userCod, userId, firstName, lastName, editorWorkload))
            print( "---- done user --------------------------------------------");


            for (roleCod, roleId, name) in crsrRole:
                r = Role( id = roleCod, roleId = roleId, name = name);
                r.save()
                # print("{}, {}, {}".format(roleCod, roleId, name))
                
            print( "---- done role --------------------------------------------");

            
            for (userCod, roleCod, disableFlag) in crsrUserRole:
                ur = User_Role(user_id = userCod, role_id = roleCod, disableFlag = disableFlag)
                ur.save();
                # print("{}, {}, {}".format(userCod, roleCod, disableFlag))
            
            print( "---- done user_role --------------------------------------------");

            
            for (editorCod, keywordCod, w) in crsrEditorKeywords:
                kwdw = Editor_Keyword( editor_id = editorCod, keyword_id = keywordCod, weight = w)
                kwdw.save()
              
            print( "---- done editor_keywords --------------------------------------------");

            
            print( "---- start loading document --------------------------------------------");
            idx=0
            for (documentCod, preprintid) in crsrDocument:
                idx = idx + 1
                # print( "Document (count: {})".format(idx) );
                doc = Document(id=documentCod, preprintid=preprintid)
                doc.save();
            print( "---- done document --------------------------------------------");
            

            print("---- start loading version --------------------------------------------");
            idx = 0;
            for (versionCod, versionNumber, documentCod) in crsrVersion:
                idx = idx + 1
                ver = Version(id = versionCod, version_number = versionNumber, document_id=documentCod)
                ver.save()
                # print("Version(count: {}): {}, {}, {}".format(idx, versionCod, versionNumber, documentCod))
                # print("Version(count: {})".format(idx))
            print( "---- done version --------------------------------------------");


            print("---- start loading action_history --------------------------------------------");
            idx = 0;
            for (actHistCod, versionCod, actionCod, agentCod, userCod, realAgentCod, actionDate) in crsrActHist:
                idx = idx + 1
                ah = Action_History( id = actHistCod, version_id = versionCod, actionCod = actionCod, agentCod_id = agentCod, userCod_id = userCod, realAgentCod_id = realAgentCod, actionDate = actionDate)
                ah.save()
                # print("{}, {}, {}, {}, {}, {}, {}".format(actHistCod, versionCod, actionCod, agentCod, userCod, realAgentCod, actionDate))
                print("Action_History(count: {})".format(idx))
                
            print("---- done action_history ----------------------------------------");
            print("number_of_rows:", number_of_rows);
            
            #record = cursor.fetchone()
            #print("You're connected to database: ", record)
            
    except Error as e:
        print("Error while connecting to MySQL", e)
        
    finally:
        if c.is_connected():
            crsrKGroup.close()
            crsrKSubgroup.close()
            crsrKeyword.close()
            crsrUser.close()
            crsrUserRole.close()
            crsrRole.close()
            crsrActHist.close()
            crsrDocument.close()
            crsrVersion.close()            
            c.close()
            print("MySQL connection is closed")
            
    # use the connection.cursor method
    return HttpResponseRedirect(reverse('medialab_keywords:kwds_ldd', args=()))

def editor_assignment_ui(request):
    context={ }
    return render(request, 'medialab_keywords/editor_assignment_ui.html', context )

def editor_assignment_service(request):
    
    x = getDocument3()
    
    [assignedEditorCode, assignmentReport] = assign_editor(x);
    
    context={
        'assignedEditor': assignedEditorCode,
        'assignmentReport': assignmentReport
    }
    return render(request, 'medialab_keywords/assignment_result.html', context)


def keywords_loaded(request):
    context={ }
    return render(request, 'medialab_keywords/keywords_loaded.html', context)

    
