import pytest
import requests
import datetime
import time


def set_expiry(minutes_from_now):
    return (datetime.datetime.utcnow() + datetime.timedelta(minutes = minutes_from_now)
            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def test_piazza():
    '''
    Tests multiple test cases outlined in the Piazza coursework
    Throughout, the reading of 'all available posts' is all posts i.e. whether
    active or not.

    Returns
    -------
    None.

    '''
    #test 1 objective: Olga, Nick Mary and Nestor register and are able 
    #to access the Piazza API
    
    url1 = "http://10.61.64.65:8000/authentication/register/"
    
    Olga_user_details= {"username": "Olga",
                        "password": "1234abcd"}
    
    Nick_user_details= {"username": "Nick",
                        "password": "1234abcd"}
    
    Mary_user_details= {"username": "Mary",
                        "password": "1234abcd"}
    
    Nestor_user_details= {"username": "Nestor",
                        "password": "1234abcd"}

    json_response_list_1 = []
    json_status_list_1 = []
    
    for user_data in [Olga_user_details, Nick_user_details, 
                      Mary_user_details, Nestor_user_details]:
        response = requests.post(url1, data = user_data)
        json_response_list_1.append(response.json())
        json_status_list_1.append(response.status_code)
    
    #test1 result:
    for json_status in json_status_list_1:
        assert str(json_status)[0] == '2'


    #test 2 objective: Olga, Nick Mary and Nestor use the oAuth v2 authorisation service to 
    # register and get their tokens.
    # Here I could not easily distinguish objective from test 1
    # but I assume test is that they can successfully refresh their tokens
    
    url2 = "http://10.61.64.65:8000/authentication/token/"
    
    json_response_list_2 = []
    json_status_list_2 = []
    
    for user_data in [Olga_user_details, Nick_user_details, Mary_user_details, Nestor_user_details]:
        response = requests.post(url2, data = user_data)
        json_response_list_2.append(response.json())
        json_status_list_2.append(response.status_code)

    #test2 result:
    for json_status in json_status_list_2:
        assert str(json_status)[0] == '2'

    #test 3 Olga makes a call to the API without using her token. This call should
    # be unsuccessful as the user is unauthorised.
    
    message_list_create_url = "http://10.61.64.65:8000/piazza/message/"
    
    response = requests.get(message_list_create_url)
    json_response_3 = response.json()
    json_status_3 = response.status_code
    
    #test3 result:
    assert str(json_status_3)[0] == '4'


    #test 4 Olga posts a message in the Tech topic with an exipration time 
    #(e.g. 5 min) using her token. After the end of the expiration time, the 
    # message will not accept any further user interactions (likes, dislikes or 
    #comments).
    
    message_4_data = {'message_heading': 'test4 heading',
                      'message_body': 'test4 body',
                      'message_topics': [1],
                      'message_expires': set_expiry(5)}
                        
    message_4_headers = {'Authorization': 'Bearer ' + str(
        json_response_list_2[0]['access_token'])}
    
    response = requests.post(message_list_create_url, 
                                 headers = message_4_headers,
                                data = message_4_data) 
    json_response_4 = response.json()
    json_status_4 = response.status_code
    
    #test4 result:
    assert str(json_status_4)[0] == '2'
    


    #test 5 Nick posts a message in the Tech topic with an expiration time using 
    # his token.
    
    message_5_data = {'message_heading': 'test5 heading',
                      'message_body': 'test5 body',
                      'message_topics': [1]}
    message_5_headers = {'Authorization': 'Bearer '+str(json_response_list_2[1]['access_token'])}
    
    response = requests.post(message_list_create_url, headers = message_5_headers, 
                             data = message_5_data) 
    json_response_5 = response.json()
    json_status_5 = response.status_code
    
    #test5 result:
    assert str(json_status_5)[0] == '2'

    #test 6 Mary posts a message in the Tech topic with an expiration time using 
    # her token.
    message_6_data = {'message_heading': 'test6 heading',
                      'message_body': 'test6 body',
                      'message_topics': [1],
                      'message_expires': set_expiry(5)}
    message_6_headers = {'Authorization': 'Bearer '+str(json_response_list_2[2]['access_token'])}
    
    response = requests.post(message_list_create_url, headers = message_6_headers, 
                             data = message_6_data) 
    json_response_6 = response.json()
    json_status_6 = response.status_code
    
    #test6 result:
    assert str(json_status_6)[0] == '2'


    #test 7 Nick and Olga browse all the available posts in the Tech topic, there
    # should be three posts available with zero likes & dislikes and no comments.
    
    message_list_create_url_filter_tech = message_list_create_url+'?message_topic=1'
    message_7_headers = {'Authorization': 'Bearer '+str(json_response_list_2[1]['access_token'])}
    
    response = requests.get(message_list_create_url_filter_tech, headers = message_7_headers) 
    
    json_response_7 = response.json()
    json_status_7 = response.status_code
    
    #test7 result:
    assert str(json_status_7)[0] == '2'
    assert len(json_response_7) == 3
    for post in json_response_7:
        assert post['num_reactions'] == 0
        assert len(post['comments']) == 0


    #test 8 Nick and Olga 'like' Mary's post in the Tech topic.
    reaction_list_create_url = "http://10.61.64.65:8000/piazza/reaction/"
    json_response_8 = []
    for user in [1,0]:
        message_8_headers = {'Authorization': 'Bearer '+str(json_response_list_2[user]['access_token'])}
        reaction_8_data = {'reaction': 'Like', 'message_id': json_response_6['message_id']}
        response = requests.post(reaction_list_create_url, headers = message_8_headers, \
                                 data= reaction_8_data)
        json_response_8.append(response.json())
        json_status_8 = response.status_code
        #test 8 results
        assert str(json_status_8)[0] == '2' 


    #test 9 Nestor 'likes' Nick's post and 'dislikes' Mary's in the Tech topic.
    reaction_list_create_url = "http://10.61.64.65:8000/piazza/reaction/"
    
    message_9_headers = {'Authorization': 'Bearer '+str(json_response_list_2[3]['access_token'])}
    reaction_9a_data = {'reaction': 'Dislike', 'message_id': json_response_6['message_id']}
    response = requests.post(reaction_list_create_url, headers = message_9_headers, \
                             data= reaction_9a_data)
    json_response_9a = response.json()
    json_status_9a = response.status_code
    assert str(json_status_9a)[0] == '2'

    reaction_9b_data = {'reaction': 'Like', 'message_id': json_response_5['message_id']}
    response = requests.post(reaction_list_create_url, headers = message_9_headers, \
                             data= reaction_9b_data)
    json_response_9b = response.json()
    json_status_9b = response.status_code
    assert str(json_status_9b)[0] == '2'


    #test 10 Nick browses all the available posts in the Tech topic, there
    # should be three posts available: Mary's (2 likes 1 dislike), Nick's (1 like),
    # Olgas (0 likes & dislikes) and all have no comments.
    
    message_list_create_url_filter_tech = message_list_create_url+'?message_topic=1'
    message_10_headers = {'Authorization': 'Bearer '+str(json_response_list_2[1]['access_token'])}
    
    response = requests.get(message_list_create_url_filter_tech, headers = message_10_headers) 
    
    json_response_10 = response.json()
    json_status_10 = response.status_code
    
    #test10 result:
    assert str(json_status_10)[0] == '2'
    assert len(json_response_10) == 3
    expected_reactions = [3, 1,0]
    for i in range(3):
        assert json_response_10[i]['num_reactions'] == expected_reactions[i]
        assert len(json_response_10[i]['comments']) == 0 



    #test 11 Mary likes her post in the Tech topic. This call should be unsuccessful
        # as in Piazza a post owner cannot like their own messages.        
    
    message_11_headers = {'Authorization': 'Bearer '+str(json_response_list_2[2]['access_token'])}
    reaction_11_data = {'reaction': 'Like', 'message_id': json_response_6['message_id']}
    response = requests.post(reaction_list_create_url, headers = message_11_headers, \
                             data= reaction_11_data)
    json_response_11 = response.json()
    json_status_11 = response.status_code
    
    #test 11 results:
    assert str(json_status_11)[0] == '4'
    
    
    
    #test 12 Nick and Olga comment on Mary's post in the Tech topic in a round-robin
    # fashion (one after the other adding at least 2 comments each)
    
    message_list_create_comment = "http://10.61.64.65:8000/piazza/comment/"
    
    json_response_12 = []
    user=1
    for count in range(4):
    
        message_12_headers = {'Authorization': 'Bearer '+str(json_response_list_2[user]['access_token'])}
        message_12_data = {'comment': 'test12 comment ' + str(count), \
                          'message_id': json_response_6['message_id']}
        response = requests.post(message_list_create_comment, headers = message_12_headers, \
                                 data= message_12_data) 
        json_response_12.append(response.json())
        json_status_12 = response.status_code
        if count % 2 == 0: user-=1 
        else: user+=1
        
        # test 12 result
        assert str(json_status_12)[0] == '2'
        

    #test 13 Nick browses all the available posts in the Tech topic, at this stage
    # he can see the number of likes and dislikes of each post and the comments made.
    
    message_list_create_url_filter_tech = message_list_create_url+'?message_topic=1'
    message_13_headers = {'Authorization': 'Bearer '+str(json_response_list_2[1]['access_token'])}
    response = requests.get(message_list_create_url_filter_tech, headers = message_13_headers) 
    json_response_13 = response.json()
    
    json_status_13 = response.status_code
    
    # test 13 result
    assert str(json_status_13)[0] == '2'



    #test 14 Nestor posts a message in the Health topic with an expiration time using 
    # her token.
    message_14_data = {'message_heading': 'test14 heading',
                      'message_body': 'test14 body',
                      'message_expires': set_expiry(1),
                      'message_topics': [2]}
    message_14_headers = {'Authorization': 'Bearer '+str(json_response_list_2[3]['access_token'])}
    response = requests.post(message_list_create_url, headers = message_14_headers, 
                             data = message_14_data) 
    json_response_14 = response.json()
    
    json_status_14 = response.status_code
    
    # test 14 result
    assert str(json_status_14)[0] == '2'


    #test 15 Mary browses all the available posts in the Health topic, at this stage
    # she can see only Nestor's post.
    
    message_list_create_url_filter_health = message_list_create_url+'?message_topic=2'
    message_15_headers = {'Authorization': 'Bearer '+str(json_response_list_2[2]['access_token'])}
    
    response = requests.get(message_list_create_url_filter_health, headers = message_15_headers) 
    
    json_response_15 = response.json()
    json_status_15 = response.status_code
    
    # test 15 result
    assert str(json_status_15)[0] == '2'
    assert len(json_response_15) == 1

    
    #test 16 Mary posts a comment on Nestor's message in the Health topic.
    message_list_create_comment = "http://10.61.64.65:8000/piazza/comment/"
    
    message_16_headers = {'Authorization': 'Bearer '+str(json_response_list_2[2]['access_token'])}
    message_16_data = {'comment': 'test16 comment',
                      'message_id': json_response_14['message_id']}
    response = requests.post(message_list_create_comment, headers = message_16_headers,
                             data= message_16_data) 
    json_response_16 = response.json()
    json_status_16 = response.status_code
    
    # test 16 result
    assert str(json_status_16)[0] == '2'


    
    #test 17 Mary dislikes Nestor's post in the Health topic after the end of post 
    # expiration time. This should fail. 

    time.sleep(60)
    message_17_headers = {'Authorization': 'Bearer '+str(json_response_list_2[2]['access_token'])}
    reaction_17_data = {'reaction': 'Dislike', 'message_id': json_response_14['message_id']}
    
    response = requests.post(reaction_list_create_url, headers = message_17_headers, \
                             data= reaction_17_data)
    
    json_response_17 = response.json()
    json_status_17 = response.status_code
    
    # test 17 result
    assert str(json_status_17)[0] == '4'
    

    #test 18 Nestor browses all the messages in the Health topic, there should only
    # be one (his own) with one comment (Mary's)
    
    message_list_create_url_filter_health = message_list_create_url+'?message_topic=2'
    message_18_headers = {'Authorization': 'Bearer '+str(json_response_list_2[3]['access_token'])}
    
    response = requests.get(message_list_create_url_filter_health, headers = message_18_headers) 
    
    json_response_18 = response.json()
    json_status_18 = response.status_code
    
    # test 18 result
    assert str(json_status_18)[0] == '2'
    assert len(json_response_18) == 1
    assert json_response_18[0]['num_reactions'] == 0
    assert len(json_response_18[0]['comments']) == 1


    #test 19 Nick browses all the expired messages in the Sport topic, these should 
    # be empty
    
    message_list_create_url_filter_sport = message_list_create_url+'?message_topic=3&message_active=false'
    message_19_headers = {'Authorization': 'Bearer '+str(json_response_list_2[1]['access_token'])}
    
    response = requests.get(message_list_create_url_filter_sport, headers = message_19_headers) 
    
    json_response_19 = response.json()
    json_status_19 = response.status_code
    
    # test 19 result
    assert str(json_status_19)[0] == '2'
    assert len(json_response_19) == 0


    #test 20 Nestor queries for an active post having the highest interest (max sum
    # of likes and dislikes) in the Tech topic. This should be Mary's post.
    
    message_list_create_url_filter_tech_active_max = message_list_create_url+ \
        '?message_topic=1&message_active=true&message_most_reactions=true'
    message_20_headers = {'Authorization': 'Bearer '+str(json_response_list_2[3]['access_token'])}
    
    response = requests.get(message_list_create_url_filter_tech_active_max, headers = message_20_headers) 
    
    json_response_20 = response.json()
    json_status_20 = response.status_code
    
    # test 20 result
    assert str(json_status_20)[0] == '2'
    assert len(json_response_20) == 1
    assert json_response_20[0]['message_id'] ==json_response_6['message_id']


