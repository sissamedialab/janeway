
1. To load the JHEP keywords in your database use:

    URL: http://localhost:8089/XTEST/medialab_keywords/keywords_management
    urls.py:  ^keywords_management$
    
2. In views.py:

     load_keywords - loads the keywords in the JHEP database in your database (configured
                     in settings.py)
                     
3. To test the editor assignment:

     - if necessary go to the URL at step 1 above to load your database and press the
       button load keywords;

     - go to
     
          http://localhost:8089/XTEST/medialab_keywords/editor_assignment_ui

       and press the button

            "Assign editor"

       Nota:

           il documento per cui viene fatta l'assegnazione e` inizializzato in
           eas.getDocument3()
       
4. L'algoritmo di assegnazione all'editor e` implementato in eas.py nella
   funzione assign_editor;

