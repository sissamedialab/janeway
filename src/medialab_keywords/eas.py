from .models import KeywordGroup
from .models import KeywordSubgroup
from .models import Keyword
from .models import User
from .models import Role
from .models import User_Role
from .models import Action_History
from .models import Editor_Keyword
from .models import Document

from django.db import connection
from django.db import reset_queries
import datetime
import math
import random



def list_of_keyword_id(list_of_keywords):
    assigned_keyword_to_keyword_id = lambda ak: ak.keyword_cod
    return list(map( assigned_keyword_to_keyword_id, list_of_keywords))



def get_number_of_assignments_starting_with_date(u, d):
    
    # NOTES:
    # - (TODO) It is necessary to remove from this QuerySet the set
    #   those that were withdrawn before the editor was able to act.

    # action ids in WjApp that are counted as editor assignents
    #
    # ADMIN_ASS_N_ED =  4
    # ED_SEL_N_ED    = 11
    # SYS_ASS_ED     = 20
    
    assignment_actions = [4, 11, 20]
    
    # print( "start_date.year: ", d.year);
    # print( "start_date.month: ", d.month);
    # print( "start_date.day: ", d.day);

    return Document.objects.filter(
        version__action_history__actionDate__gte = d,
        version__action_history__userCod = u,
        version__action_history__actionCod__in = assignment_actions
    ).distinct().count()



def get_keyword_suitability(editor, doc_keywords):
    
    # reset_queries() ## ____REMOVE_LINE____

    list_of_keywords = list_of_keyword_id(doc_keywords)

    # get all editor keywords that are in list_of_keywords
    #
    editor_keywords = Editor_Keyword.objects.filter(editor = editor, keyword__in = list_of_keywords)
    
    stblt = 0
    
    for ek in editor_keywords:
        ed_kwd_id = ek.keyword_id
        ed_kwd_weight = ek.weight
        
        for dk in doc_keywords:
            if ed_kwd_id == dk.keyword_cod:
                stblt = stblt + ed_kwd_weight * dk.weight
                print( str(ek) + "kid: " + str(ed_kwd_id) + " ed weight:" + str(ed_kwd_weight) + "; doc weight: " + str(dk.weight) );
                break;
            
    
    # print( "sum:" + str(stblt) );                 ## ____REMOVE_LINE____    
    # print( str(connection.queries) + "\n\n" )     ## ____REMOVE_LINE____
        
    return stblt;



def assign_editor(doc):
    # Notes:
    # - (TODO) It is necessary to remove from the list of editors
    #   those that are found in the authors metadata field.
    # - (TODO) Mob name must be added for JSTAT (look for MOB_NAME)
    #

    # reset_queries()   ## ____REMOVE_LINE____
    
    use_sections = False
    MOB_NAME = "Test MobName"
    
    tdy = datetime.date.today()

    report = "Report on the editor assignment algorithm for " + doc.preprint_id + ".\n"
    report = report + "\n";
    fn1="*  the number of articles that were assigned to the editor starting with the first" + "\n" + "   day of the current month.\n"
    fn2="** the number of articles that were assigned to the editor during the last 30 days."
    footer = "\nEND OF REPORT" + "\n"

    # begin
    #
    # retrieves all users with the following characteristics:
    #     - have the editor role;
    #     - their editor role is not disabled;
    #     - have keywords in the set of keywords associated with the document;
    #     - the weight of the editor for the associated keywords is not 0;
    #     - who are not the corresponding authors of the preprint;
    #     - distinct rows
    # 
    # NOTES:
    #     - the query should also eliminate the past editors
    #
    associated_kwd_ids = list_of_keyword_id(doc.list_of_keywords)    
    # print( associated_kwd_ids )   ## ____REMOVE_LINE____
    l0 = User.objects.filter(
        user_role__role__roleId = "EDT",
        user_role__disableFlag = 0,
        editor_keyword__keyword__in = associated_kwd_ids,
        editor_keyword__weight__gt = 0
    ).exclude(pk = doc.author_cod).order_by('pk').distinct();
    #
    # end
    
    # print( connection.queries );    ## ____REMOVE_LINE____

    if not l0.exists():
        report = report + "The article keywords are not associated with any editor.\n" + footer;
        return [ -1, report ];

    report = report + "\n";
    report = report + "Comprehensive list of editors associated with the selected keywords:\n\n";

    if use_sections:
        report = report + "         max-workload    current workload(*)    Name                            Director                        Status\n"
        report = report + "        ------------------------------------------------------------------------------------------------------------------\n"
    else:
        report = report + "         max-workload    current workload(*)    Name                            Status\n"
        report = report + "        ---------------------------------------------------------------------------------\n"

    current_month_start_date = datetime.date(tdy.year, tdy.month, 1);
    l1 = []
    
    for editor in l0:
        # reset_queries() ## ____REMOVE_LINE____

        current_month_workload = get_number_of_assignments_starting_with_date(editor, current_month_start_date);
        
        report = report + "        " + "    "  + ("{0: >6}           {1: >6}             {2: <32}".format(str(editor.editorWorkload), str(current_month_workload), editor.firstName + " " + editor.lastName));
        if use_sections:
            report = report + "{0: <32}".format(MOB_NAME)

        if editor.editorWorkload > current_month_workload:
            report = report + "accepted"
            l1.append(editor);
        else:
            report = report + "eliminated [workload reached]"
            
        report = report + "\n"
        
        # print( connection.queries )     ## ____REMOVE_LINE____

    if len(l1) == 0:
        report = report + "\n"
        report = report + "No editor is suggested because all candidate editors have reached their workload.\n" + "\n" + fn1 + footer;
        return [ -1, report ];

       
    # begin
    #
    # compute the following:
    #
    #    - the keyword suitability for each editor
    #    - the number of articles assigned to the editor during the last 30 days
    #    - the maximum value of the keyword suitability.
    #
    #      We use this value to scale all calculated keyword suitabilities to the
    #      0..16 interval.
    #
    #      The interval is 0..16 because the gaussian function we compute below
    #      10/(1+exp(-x + 8.5)) + x/10 has a minimum of almost 0 in x == 0 and
    #      a maximum of almost 10 in x == 16
    #
    thirty_days_ago = tdy - datetime.timedelta(days = 30)
    
    if len(l1) > 1:
        
        max_kwd_suitability = -1;
    
        for editor in l1:
            editor.kwd_suitability = get_keyword_suitability(editor, doc.list_of_keywords);
            editor.thrity_days_workload = get_number_of_assignments_starting_with_date(editor, thirty_days_ago);

            if editor.kwd_suitability > max_kwd_suitability:
                max_kwd_suitability = editor.kwd_suitability
            
        if max_kwd_suitability == 0:
            max_kwd_suitability = 1;
                    
        for editor in l1:
            editor.scaled_suitability = ( float(editor.kwd_suitability) / float(max_kwd_suitability) ) * 16.0
            editor.gaussian_suitability = 10.0/(1 + math.exp(-editor.scaled_suitability + 8.5))
            editor.suitability=editor.gaussian_suitability - ( float(editor.thrity_days_workload) / 2.0 )

        l1.sort( reverse=True, key = lambda x: x.suitability )
        
    else:
        l1[0].kwd_suitability = get_keyword_suitability(l1[0], doc.list_of_keywords);
        l1[0].thrity_days_workload = get_number_of_assignments_starting_with_date(l1[0], thirty_days_ago);
        
    #
    # end

    report = report + "\n"
    report = report + "Candidates for the submission in question. Please cross-check suitability (scientific\ncompetence) with last-month workload:\n\n";
    report = report + "         suitability  last-month workload(**)   Name                            \n";
    report = report + "        ------------------------------------------------------------------------\n";

    for editor in l1:
        report = report + \
            "        " +  "    " + "{0: >6}             {1: >6}           {2: <32}".format(editor.kwd_suitability, editor.thrity_days_workload, editor.firstName + " " + editor.lastName) + "\n"

    chosen_index = 0

    if len(l1) > 1:
        if l1[0].suitability == l1[1].suitability:
            i = 1;
            for i in range(2, len(l1) - 1):
                if l1[i].suitability != l1[0].suitability:
                    i = i - 1
                    break
            chosen_index = random.randint(0, i)
            
    report = report + "\n" + "Chosen editor: " + l1[chosen_index].firstName + " " + l1[chosen_index].lastName +  "\n\n" + fn1 + fn2 + "\n" + footer;
    return [ l1[chosen_index].id, report ];    



def getDocument1():
    return XDocument( "t1", "JHEP_004P_0608", [], 66 );



def getDocument2():
    return XDocument( "t2", "JHEP_004P_0608", [], 43 );



def getDocument3():
    # k1 = AssignedKeyword(305, 20)
    # k2 = AssignedKeyword(254, 60)
    # k3 = AssignedKeyword(302, 60)
    
    # l = [k1, k2, k3]

    # JHEP Assignment as of 2022/06/27
    # JHEP_237P_0622
    k1 = AssignedKeyword(25, 50)
    k2 = AssignedKeyword(27, 50)
    k3 = AssignedKeyword(64, 100)
    k4 = AssignedKeyword(130, 100)
    l = [k1, k2, k3, k4]

    # JHEP Assignment as of 2022/06/27
    # JHEP_236P_0622
    # k1 = AssignedKeyword(267, 20)
    # k2 = AssignedKeyword(284, 60)
    # k3 = AssignedKeyword(297, 60)
    # l = [k1, k2, k3]

    # A single editor has this keyword
    # As of 2022/06/27 the assigned editor has reached his monthly workload.
    # k1 = AssignedKeyword(272, 60)
    # l = [k1]


    # A single editor has this keyword (Adam Schwimer)
    # 
    # k1 = AssignedKeyword(313, 60)
    # l = [k1]

    # The keyword with the code 246 is share by two editors. Both of them
    # have weight 100 for this keyword.
    #
    # k1 = AssignedKeyword(232, 100)
    # k2 = AssignedKeyword(309, 100)
    # l = [k1, k2]
    
    # No editor with these keywords
    # 
    # k1 = AssignedKeyword(1267, 20)
    # k2 = AssignedKeyword(1284, 60)
    # k3 = AssignedKeyword(1297, 60)
    # l = [k1, k2, k3]
    
    return XDocument( "t3", "JHEP_004P_0608", l, 88 );



class AssignedKeyword:
    def __init__(self, keyword_cod, weight):
        self.keyword_cod = keyword_cod
        self.weight = weight
        
    def __str__(self):
        return "id:" + str(self.keyword_cod) + "(weight:" + str(self.weight) + ")"



class XDocument:
    def __init__(self, title, preprint_id, list_of_keywords, author_cod):
        self.title = title
        self.preprint_id = preprint_id
        self.list_of_keywords = list_of_keywords
        self.author_cod=author_cod

    
    
