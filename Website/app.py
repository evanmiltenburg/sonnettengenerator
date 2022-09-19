from flask import Flask, session, render_template, request, redirect
import random
from sonnet import sonnet, random_sonnet, get_selection, get_update_set, get_sonnet_using_words
from metadata import enrich_sonnet
import datetime
import json
import glob


app = Flask(__name__)

# Setup the secret key and the environment 
app.config.update(SECRET_KEY='ksjghsdkvfkugk958305482948309')


def permakey():
    "Key for the permalink."
    delta = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    millisec = int(delta.total_seconds() * 1000)
    random_component = str(random.randint(0,999)).zfill(3)
    return random_component + str(millisec)


def write_sonnet(sonnet, key):
    "Write sonnet to disk."
    with open(f'./static/sonnets/{key}.json', 'w') as f:
        json.dump(sonnet,f)

        
def load_sonnet(key):
    "Read sonnet from disk."
    with open(f'./static/sonnets/{key}.json', 'r') as f:
        data = json.load(f)
    return data


@app.route('/')
def hello():
    subset, corpus, pattern, base_sonnet = random_sonnet()
    sonnet_id = permakey()
    write_sonnet(base_sonnet, sonnet_id)
    enriched_sonnet = enrich_sonnet(base_sonnet)
    if corpus == 'combination':
        corpus = "een combinatie van DBNL en Wikipedia"
    return render_template("index.htm", 
                           subset=subset, 
                           corpus=corpus, 
                           pattern=pattern, 
                           sonnet=enriched_sonnet,
                           sonnet_id = sonnet_id)


@app.route('/random/', methods=['GET','POST'])
def present_random_sonnet():
    if request.method == 'GET':
        base_sonnet = sonnet(corpus="combination", 
                             subset='all', 
                             pattern="abba abba cdc dcd")
        sonnet_id = permakey()
        write_sonnet(base_sonnet, sonnet_id)
        enriched_sonnet = enrich_sonnet(base_sonnet)
        return render_template("random-form.htm", 
                               sonnet=enriched_sonnet,
                               corpus="combination", 
                               subset='all', 
                               pattern="abba abba cdc dcd",
                               sonnet_id = sonnet_id)
    else:
        corpus = request.form['corpus']
        subset = request.form['syllables'] 
        pattern = request.form['pattern']
        base_sonnet=sonnet(corpus=corpus, subset=subset, pattern=pattern)
        sonnet_id = permakey()
        write_sonnet(base_sonnet, sonnet_id)
        enriched_sonnet = enrich_sonnet(base_sonnet)
        return render_template("random-form.htm", 
                               sonnet=enriched_sonnet,
                               corpus=corpus, 
                               subset=subset,
                               pattern=pattern,
                               sonnet_id = sonnet_id)


@app.route('/zelf/')
def step_one():
    return render_template("step-one.htm")

@app.route('/zelfbouw/', methods=['POST'])
def step_two():
    if request.form['step'] == '1':
        session['corpus'] = request.form['corpus']
        session['subset'] = request.form['syllables'] 
        session['pattern'] = request.form['pattern']
        session['letters'] = sorted(set(session['pattern']) - {' '})
        session['choices'] = dict()
        session['used_rhymes'] = []
        session['selected_words'] = []
        
        suggestions = get_selection(letter=session['letters'][0], 
                                    used_rhymes=set(session['used_rhymes']), 
                                    pattern=session['pattern'], 
                                    corpus=session['corpus'], 
                                    subset=session['subset'])
        
        return render_template('step-n.htm',
                               current_letter=session['letters'][0],
                               suggestions=suggestions)
    else:
        selected = request.form['selectie']
        letter = request.form['letter']
        rhymes = get_update_set(selected, 
                                corpus=session['corpus'], 
                                subset=session['subset'])
        session['used_rhymes'] += list(rhymes)
        session['selected_words'] += [selected]
        session['choices'][letter] = [selected] + list(rhymes - {selected})
        previous_index = session['letters'].index(letter)
        print(previous_index)
        if previous_index < (len(session['letters']) - 1):
            current_index = previous_index + 1
            current_letter = session['letters'][current_index]
            suggestions = get_selection(letter=current_letter, 
                                used_rhymes=session['used_rhymes'], 
                                pattern=session['pattern'], 
                                corpus=session['corpus'], 
                                subset=session['subset'])
            return render_template('step-n.htm',
                                   current_letter=current_letter,
                                   suggestions=suggestions,
                                   selected_words=', '.join(session['selected_words']))
        else:
            return redirect('/zelf-done/')


@app.route('/zelf-done/')
def done_building():
    corpus = session['corpus']
    if corpus == 'combination':
        corpus = "een combinatie van DBNL en Wikipedia"
    base_sonnet = get_sonnet_using_words(session['choices'], 
                                    session['corpus'], 
                                    session['subset'], 
                                    session['pattern'])
    sonnet_id = permakey()
    write_sonnet(base_sonnet, sonnet_id)
    enriched_sonnet = enrich_sonnet(base_sonnet)
    return render_template("final-sonnet.htm",
                           sonnet = enriched_sonnet,
                           corpus=corpus, 
                           subset=session['subset'],
                           pattern=session['pattern'],
                           selected_words=', '.join(session['selected_words']),
                           sonnet_id = sonnet_id)


@app.route('/over/')
def over():
    return render_template("over.htm")


@app.route('/perma/<sonnet_id>')
def render_sonnet(sonnet_id):
    all_sonnets = glob.glob('./static/sonnets/*.json')
    filename = f'./static/sonnets/{sonnet_id}.json'
    base_sonnet = load_sonnet(sonnet_id)
    enriched_sonnet = enrich_sonnet(base_sonnet)
    return render_template("perma.htm",
                           sonnet = enriched_sonnet,
                           sonnet_id = sonnet_id)


if __name__ == '__main__':
    app.run(debug=True)