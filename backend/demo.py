from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

demo_bp = Blueprint('demo', __name__, url_prefix='/api/demo')

# Demo user personas with their viewing history
DEMO_USERS = {
    'sarah': {
        'id': 'sarah',
        'name': 'Sarah',
        'subtitle': 'The Sci-Fi Enthusiast',
        'description': 'Loves: Inception, Interstellar, The Matrix',
        'avatar_color': 'bg-purple-600',
        'initial_movies': [
            {'id': 27205, 'title': 'Inception', 'rating': 5, 'year': 2010, 'poster_path': '/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg'},
            {'id': 157336, 'title': 'Interstellar', 'rating': 5, 'year': 2014, 'poster_path': '/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg'},
            {'id': 603, 'title': 'The Matrix', 'rating': 5, 'year': 1999, 'poster_path': '/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg'},
            {'id': 329865, 'title': 'Arrival', 'rating': 4, 'year': 2016, 'poster_path': '/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg'},
            {'id': 335984, 'title': 'Blade Runner 2049', 'rating': 4, 'year': 2017, 'poster_path': '/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg'},
            {'id': 272, 'title': 'Batman Begins', 'rating': 4, 'year': 2005, 'poster_path': '/1P3ZyEq02wcTMd3iE4ebtLvncvH.jpg'},
            {'id': 680, 'title': 'Pulp Fiction', 'rating': 4, 'year': 1994, 'poster_path': '/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'},
            {'id': 13, 'title': 'Forrest Gump', 'rating': 4, 'year': 1994, 'poster_path': '/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg'},
            {'id': 424, 'title': "Schindler's List", 'rating': 5, 'year': 1993, 'poster_path': '/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg'},
            {'id': 550, 'title': 'Fight Club', 'rating': 4, 'year': 1999, 'poster_path': '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'},
            {'id': 78, 'title': 'Blade Runner', 'rating': 4, 'year': 1982, 'poster_path': '/63N9uy8nd9j7Eog2axPQ8lbr3Wj.jpg'},
            {'id': 129, 'title': 'Spirited Away', 'rating': 4, 'year': 2001, 'poster_path': '/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg'},
            {'id': 496243, 'title': 'Parasite', 'rating': 5, 'year': 2019, 'poster_path': '/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg'},
        ],
        'rated_movies': []
    },
    'james': {
        'id': 'james',
        'name': 'James',
        'subtitle': 'The Action Junkie',
        'description': 'Loves: The Dark Knight, Mad Max, John Wick',
        'avatar_color': 'bg-red-600',
        'initial_movies': [
            {'id': 155, 'title': 'The Dark Knight', 'rating': 5, 'year': 2008, 'poster_path': '/qJ2tW6WMUDux911r6m7haRef0WH.jpg'},
            {'id': 76341, 'title': 'Mad Max: Fury Road', 'rating': 5, 'year': 2015, 'poster_path': '/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg'},
            {'id': 245891, 'title': 'John Wick', 'rating': 5, 'year': 2014, 'poster_path': '/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg'},
            {'id': 198, 'title': 'Gladiator', 'rating': 4, 'year': 2000, 'poster_path': '/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg'},
            {'id': 807, 'title': 'Se7en', 'rating': 4, 'year': 1995, 'poster_path': '/6yoghtyTpznpBik8EngEmJskVUO.jpg'},
            {'id': 1124, 'title': 'The Prestige', 'rating': 4, 'year': 2006, 'poster_path': '/tRNlZbgNCNOpLpbPEz5L8G8A0JN.jpg'},
            {'id': 280, 'title': 'Terminator 2', 'rating': 5, 'year': 1991, 'poster_path': '/5M0j0B18abtBI5gi2RhfjjurTqb.jpg'},
            {'id': 1895, 'title': 'Star Wars', 'rating': 4, 'year': 1977, 'poster_path': '/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg'},
        ],
        'rated_movies': []
    },
    'emma': {
        'id': 'emma',
        'name': 'Emma',
        'subtitle': 'The Cold-Start User',
        'description': 'Just joined. Only watched 2 movies.',
        'avatar_color': 'bg-blue-600',
        'initial_movies': [
            {'id': 278, 'title': 'The Shawshank Redemption', 'rating': 5, 'year': 1994, 'poster_path': '/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg'},
            {'id': 13, 'title': 'Forrest Gump', 'rating': 5, 'year': 1994, 'poster_path': '/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg'},
        ],
        'rated_movies': []
    }
}

# Recommendation states for each user
RECOMMENDATIONS = {
    'sarah': {
        'initial': [
            {
                'id': 466282,
                'title': 'Tenet',
                'year': 2020,
                'poster_path': '/k68nPLbIST6NP96JmTxmZijEvCA.jpg',
                'match_score': 94,
                'explanations': [
                    'You enjoyed Sci-Fi films like Inception',
                    'Shared director: Christopher Nolan',
                    'Tagged: time-manipulation, complex-narrative',
                    'Recent release from 2020s era'
                ],
                'graph_paths': [
                    'Inception → Sci-Fi → Tenet',
                    'Inception → Nolan → Tenet',
                    'Inception → "mind-bending" → Tenet'
                ]
            },
            {
                'id': 293660,
                'title': 'Deadpool',
                'year': 2016,
                'poster_path': '/3E53WEZJqP6aM84D8CckXx4pIHw.jpg',
                'match_score': 89,
                'explanations': [
                    'Action-packed like The Matrix',
                    'Modern superhero film with sci-fi elements',
                    'High-energy entertainment from 2016'
                ],
                'graph_paths': [
                    'The Matrix → action sci-fi → Deadpool',
                    'Batman Begins → superhero genre → Deadpool'
                ]
            },
            {
                'id': 299536,
                'title': 'Avengers: Infinity War',
                'year': 2018,
                'poster_path': '/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg',
                'match_score': 86,
                'explanations': [
                    'Epic sci-fi action like Interstellar scale',
                    'Tagged: space, complex-plot, ensemble',
                    'Blockbuster loved by sci-fi fans'
                ],
                'graph_paths': [
                    'Interstellar → epic scale → Infinity War',
                    'The Matrix → sci-fi action → Infinity War'
                ]
            }
        ],
        'after_tenet': [
            {
                'id': 77,
                'title': 'Memento',
                'year': 2000,
                'poster_path': '/yuNs09hvpHVU1cBTCAk9zxsL2oW.jpg',
                'match_score': 93,
                'explanations': [
                    'Another Christopher Nolan masterpiece',
                    "You've now rated 3 Nolan films highly",
                    'Non-linear narrative like Tenet and Inception'
                ],
                'graph_paths': [
                    'Tenet → Christopher Nolan → Memento',
                    'Inception → non-linear narrative → Memento',
                    'Strong Nolan cluster forming'
                ],
                'confidence': 'HIGH ↑↑↑'
            },
            {
                'id': 264660,
                'title': 'Ex Machina',
                'year': 2014,
                'poster_path': '/9goPE2IoMIXD5s3v352cCAPpV96.jpg',
                'match_score': 89,
                'explanations': [
                    'Matches your interest in AI and philosophy themes',
                    'Similar to: Blade Runner 2049, Arrival',
                    'Indie Sci-Fi from 2010s (your preferred decade)'
                ],
                'graph_paths': [
                    'Blade Runner 2049 → AI themes → Ex Machina',
                    'Arrival → philosophical sci-fi → Ex Machina'
                ]
            },
            {
                'id': 14337,
                'title': 'Primer',
                'year': 2004,
                'poster_path': '/vJorEuzfH801OZsQYZmiHb3xgcn.jpg',
                'match_score': 86,
                'explanations': [
                    'Tagged: time-travel, complex-plot',
                    'Beloved by fans of Inception and Interstellar',
                    'Cult classic in Sci-Fi genre'
                ],
                'graph_paths': [
                    'Inception → time-manipulation → Primer',
                    'Interstellar → complex narrative → Primer'
                ]
            }
        ]
    },
    'james': {
        'initial': [
            {
                'id': 353081,
                'title': 'Mission: Impossible - Fallout',
                'year': 2018,
                'poster_path': '/AkJQpZp9WoNdj7pLYSj1L0RcMMN.jpg',
                'match_score': 91,
                'explanations': [
                    'Action-packed like Mad Max and John Wick',
                    'Tagged: practical-stunts, intense-action',
                    'High-octane choreography similar to The Raid'
                ],
                'graph_paths': [
                    'John Wick → practical stunts → MI: Fallout',
                    'Mad Max → intense action → MI: Fallout',
                    'The Raid → choreography → MI: Fallout'
                ]
            },
            {
                'id': 263115,
                'title': 'Logan',
                'year': 2017,
                'poster_path': '/fnbjcRDYn6YviCcePDnGdyAkYsB.jpg',
                'match_score': 88,
                'explanations': [
                    'Gritty action with emotional depth',
                    'Similar intensity to The Dark Knight',
                    'Praised fight choreography'
                ],
                'graph_paths': [
                    'The Dark Knight → gritty action → Logan',
                    'Mad Max → intense violence → Logan'
                ]
            },
            {
                'id': 339964,
                'title': 'Baby Driver',
                'year': 2017,
                'poster_path': '/rmnQ9jKW72bHu8uKlMjPIb2VLMI.jpg',
                'match_score': 85,
                'explanations': [
                    'Stylized action with unique flair',
                    'Loved by fans of Mad Max: Fury Road',
                    '2010s action cinema at its best'
                ],
                'graph_paths': [
                    'Mad Max → stylized action → Baby Driver',
                    'John Wick → unique style → Baby Driver'
                ]
            }
        ],
        'after_prestige': [
            {
                'id': 1124,
                'title': 'The Illusionist',
                'year': 2006,
                'poster_path': '/fUfFAJPFq4DLkcLmLvhCHCGXP1G.jpg',
                'match_score': 87,
                'explanations': [
                    'Mystery-thriller like The Prestige',
                    'Tagged: magic, plot-twists',
                    'BUT also contains: period-action sequences'
                ],
                'graph_paths': [
                    'The Prestige → magic themes → The Illusionist',
                    'The Dark Knight → plot twists → The Illusionist',
                    'Action + Drama cluster bridge'
                ],
                'confidence': 'BALANCED'
            },
            {
                'id': 353081,
                'title': 'Mission: Impossible - Fallout',
                'year': 2018,
                'poster_path': '/AkJQpZp9WoNdj7pLYSj1L0RcMMN.jpg',
                'match_score': 91,
                'explanations': [
                    'Action-packed like Mad Max and John Wick',
                    'Tagged: practical-stunts, intense-action',
                    'High-octane choreography similar to The Raid'
                ],
                'graph_paths': [
                    'John Wick → practical stunts → MI: Fallout',
                    'Mad Max → intense action → MI: Fallout'
                ]
            },
            {
                'id': 263115,
                'title': 'Logan',
                'year': 2017,
                'poster_path': '/fnbjcRDYn6YviCcePDnGdyAkYsB.jpg',
                'match_score': 88,
                'explanations': [
                    'Gritty action with emotional depth',
                    'Similar intensity to The Dark Knight',
                    'Praised fight choreography'
                ],
                'graph_paths': [
                    'The Dark Knight → gritty action → Logan'
                ]
            }
        ]
    },
    'emma': {
        'initial': [
            {
                'id': 497,
                'title': 'The Green Mile',
                'year': 1999,
                'poster_path': '/velWPhVMQeQKcxggNEU8YmIo52R.jpg',
                'match_score': 92,
                'explanations': [
                    'Same director as Forrest Gump (Frank Darabont)',
                    'Similar themes: hope, redemption, human connection',
                    'Tagged: emotional, inspirational',
                    '1990s drama—matching your viewing decade'
                ],
                'graph_paths': [
                    'Forrest Gump → Frank Darabont → The Green Mile',
                    'Shawshank → redemption theme → The Green Mile',
                    'Forrest Gump → 1990s drama → The Green Mile'
                ]
            },
            {
                'id': 453,
                'title': 'A Beautiful Mind',
                'year': 2001,
                'poster_path': '/zwzWCmH72OSC9NA0ipoqw5Zjya8.jpg',
                'match_score': 89,
                'explanations': [
                    'Uplifting biographical drama',
                    'Shares emotional depth with Shawshank',
                    'Oscar-winning like both your rated films'
                ],
                'graph_paths': [
                    'Shawshank → uplifting drama → A Beautiful Mind',
                    'Forrest Gump → biographical → A Beautiful Mind'
                ]
            },
            {
                'id': 9614,
                'title': 'Good Will Hunting',
                'year': 1997,
                'poster_path': '/bABCBKYBK7A5G1x0FzoeoNfuj2.jpg',
                'match_score': 87,
                'explanations': [
                    'Emotional drama from the 1990s',
                    'Themes of personal growth and redemption',
                    'Beloved by fans of Shawshank and Forrest Gump'
                ],
                'graph_paths': [
                    'Shawshank → redemption → Good Will Hunting',
                    'Forrest Gump → 1990s → Good Will Hunting'
                ]
            }
        ],
        'after_green_mile': [
            {
                'id': 1402,
                'title': 'The Pursuit of Happyness',
                'year': 2006,
                'poster_path': '/c4TWMBZGlaQR7gViZHnWbZq2AqN.jpg',
                'match_score': 91,
                'explanations': [
                    'STRONG pattern detected: You love inspirational dramas',
                    'Themes: perseverance, father-son relationships',
                    'Emotional journey similar to all 3 of your rated films'
                ],
                'graph_paths': [
                    'Shawshank → perseverance → Pursuit of Happyness',
                    'Forrest Gump → father-son → Pursuit of Happyness',
                    'The Green Mile → hope → Pursuit of Happyness'
                ],
                'confidence': 'HIGH ↑↑↑'
            },
            {
                'id': 453,
                'title': 'A Beautiful Mind',
                'year': 2001,
                'poster_path': '/zwzWCmH72OSC9NA0ipoqw5Zjya8.jpg',
                'match_score': 89,
                'explanations': [
                    'Uplifting biographical drama',
                    'Shares emotional depth with Shawshank',
                    'Oscar-winning like both your rated films'
                ],
                'graph_paths': [
                    'Shawshank → uplifting drama → A Beautiful Mind',
                    'The Green Mile → emotional depth → A Beautiful Mind'
                ]
            },
            {
                'id': 9614,
                'title': 'Good Will Hunting',
                'year': 1997,
                'poster_path': '/bABCBKYBK7A5G1x0FzoeoNfuj2.jpg',
                'match_score': 87,
                'explanations': [
                    'Emotional drama from the 1990s',
                    'Themes of personal growth and redemption',
                    'Beloved by fans of Shawshank and Forrest Gump'
                ],
                'graph_paths': [
                    'Shawshank → redemption → Good Will Hunting',
                    'The Green Mile → hope → Good Will Hunting'
                ]
            }
        ]
    }
}


@demo_bp.route('/users', methods=['GET'])
@cross_origin()
def get_demo_users():
    """Get all demo user personas"""
    users = []
    for user_id, user_data in DEMO_USERS.items():
        users.append({
            'id': user_data['id'],
            'name': user_data['name'],
            'subtitle': user_data['subtitle'],
            'description': user_data['description'],
            'avatar_color': user_data['avatar_color'],
            'movies_watched': len(user_data['initial_movies']) + len(user_data['rated_movies'])
        })
    return jsonify({'users': users}), 200


@demo_bp.route('/user/<user_id>', methods=['GET'])
@cross_origin()
def get_user_profile(user_id):
    """Get detailed user profile with viewing history"""
    if user_id not in DEMO_USERS:
        return jsonify({'error': 'User not found'}), 404
    
    user = DEMO_USERS[user_id]
    all_movies = user['initial_movies'] + user['rated_movies']
    
    return jsonify({
        'id': user['id'],
        'name': user['name'],
        'subtitle': user['subtitle'],
        'description': user['description'],
        'avatar_color': user['avatar_color'],
        'watched_movies': all_movies,
        'total_movies': len(all_movies)
    }), 200


@demo_bp.route('/recommendations/<user_id>', methods=['GET'])
@cross_origin()
def get_recommendations(user_id):
    """Get personalized recommendations for a user"""
    if user_id not in DEMO_USERS:
        return jsonify({'error': 'User not found'}), 404
    
    user = DEMO_USERS[user_id]
    
    # Determine which recommendation state to return
    if user_id == 'sarah' and any(m['id'] == 466282 for m in user['rated_movies']):
        recs = RECOMMENDATIONS['sarah']['after_tenet']
    elif user_id == 'james' and any(m['id'] == 1124 for m in user['rated_movies']):
        recs = RECOMMENDATIONS['james']['after_prestige']
    elif user_id == 'emma' and any(m['id'] == 497 for m in user['rated_movies']):
        recs = RECOMMENDATIONS['emma']['after_green_mile']
    else:
        recs = RECOMMENDATIONS[user_id]['initial']
    
    return jsonify({
        'user_id': user_id,
        'recommendations': recs
    }), 200


@demo_bp.route('/rate-movie', methods=['POST'])
@cross_origin()
def rate_movie():
    """Rate a movie for a demo user"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'movie_id' not in data or 'rating' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_id = data['user_id']
    movie_id = data['movie_id']
    rating = data['rating']
    
    if user_id not in DEMO_USERS:
        return jsonify({'error': 'User not found'}), 404
    
    # Add movie to user's rated movies if not already there
    user = DEMO_USERS[user_id]
    if not any(m['id'] == movie_id for m in user['rated_movies']):
        # Find movie details from recommendations
        movie_details = None
        for rec_state in RECOMMENDATIONS[user_id].values():
            for rec in rec_state:
                if rec['id'] == movie_id:
                    movie_details = {
                        'id': rec['id'],
                        'title': rec['title'],
                        'rating': rating,
                        'year': rec['year']
                    }
                    break
            if movie_details:
                break
        
        if movie_details:
            user['rated_movies'].append(movie_details)
    
    return jsonify({
        'success': True,
        'message': f"Rated {movie_id} with {rating} stars"
    }), 200


@demo_bp.route('/reset/<user_id>', methods=['POST'])
@cross_origin()
def reset_user(user_id):
    """Reset a user's demo state"""
    if user_id not in DEMO_USERS:
        return jsonify({'error': 'User not found'}), 404
    
    DEMO_USERS[user_id]['rated_movies'] = []
    
    return jsonify({
        'success': True,
        'message': f"Reset {user_id}'s demo state"
    }), 200

