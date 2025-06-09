from flask import Flask, request, jsonify, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------------------------------------------------------
# DATABASE MODELS
# ------------------------------------------------------------------

class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)

    # Basic fields
    symbol = db.Column(db.String(50), nullable=True)
    entry_date = db.Column(db.String(50), nullable=True)
    exit_date = db.Column(db.String(50), nullable=True)

    # New question fields (left side, right side, and one spanning both)
    left1 = db.Column(db.Text)
    left2 = db.Column(db.Text)
    left3 = db.Column(db.Text)
    left4 = db.Column(db.Text)
    left5 = db.Column(db.Text)
    left6 = db.Column(db.Text)
    right1 = db.Column(db.Text)
    right2 = db.Column(db.Text)
    right3 = db.Column(db.Text)
    right4 = db.Column(db.Text)
    right5 = db.Column(db.Text)
    right6 = db.Column(db.Text)
    bottomQ = db.Column(db.Text)

    # Boolean field for following the plan
    do_follow_plan = db.Column(db.Boolean, default=False)

class TradeImage(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('trades.id'), nullable=False)
    pane_number = db.Column(db.Integer, nullable=False)
    blob_data = db.Column(db.LargeBinary, nullable=False)

class Setup(db.Model):
    __tablename__ = 'setups'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, default="")  # Comments or description for the setup

class SetupImage(db.Model):
    __tablename__ = 'setup_images'
    id = db.Column(db.Integer, primary_key=True)
    setup_id = db.Column(db.Integer, db.ForeignKey('setups.id'), nullable=False)
    blob_data = db.Column(db.LargeBinary, nullable=False)

# New mapping table to relate setups and tags.
class SetupTagMapping(db.Model):
    __tablename__ = 'setup_tags'
    setup_id = db.Column(db.Integer, db.ForeignKey('setups.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

# New Tag model for tag management
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Create tables for the new model as well
with app.app_context():
    db.create_all()


# ------------------------------------------------------------------
# ROUTES - SERVE THE MAIN PAGE
# ------------------------------------------------------------------
@app.route('/')
def index():
    """Serve the main HTML (Bootstrap 5) page."""
    return render_template('base.html')

@app.route('/trades')
def trades():
    """Serve the main HTML (Bootstrap 5) page."""
    return render_template('trades.html')

# Render the tag manager page.
@app.route('/tag-manager')
def tag_manager():
    return render_template('tag_manager.html')

@app.route('/setup-entry')
def setup_entry():
    return render_template('setup_entry.html')

@app.route('/setup-search')
def setup_search_page():
    """
    Render the setup search page.
    This page will list all available tags.
    """
    return render_template('setup_search.html')

@app.route('/setup-search-results')
def setup_search_results_page():
    """
    Render the setup search page.
    This page will list all available tags.
    """
    return render_template('setup_search_results.html')


# ------------------------------------------------------------------
# ROUTES - CRUD FOR TRADES
# ------------------------------------------------------------------

@app.route('/api/trades', methods=['GET'])
def get_all_trades():
    trades = Trade.query.order_by(Trade.id).all()
    data = []
    for t in trades:
        data.append({
            "id": t.id,
            "symbol": t.symbol,
            "entry_date": t.entry_date,
            "exit_date": t.exit_date,
            "left1": t.left1 or "",
            "left2": t.left2 or "",
            "left3": t.left3 or "",
            "left4": t.left4 or "",
            "left5": t.left5 or "",
            "left6": t.left6 or "",
            "right1": t.right1 or "",
            "right2": t.right2 or "",
            "right3": t.right3 or "",
            "right4": t.right4 or "",
            "right5": t.right5 or "",
            "right6": t.right6 or "",
            "bottomQ": t.bottomQ or "",
            "do_follow_plan": t.do_follow_plan or False
        })
    return jsonify(data)

@app.route('/api/trades/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    images = TradeImage.query.filter_by(record_id=trade.id).all()
    image_list = []
    for img in images:
        image_list.append({
            "id": img.id,
            "pane_number": img.pane_number
        })
    data = {
        "id": trade.id,
        "symbol": trade.symbol,
        "entry_date": trade.entry_date,
        "exit_date": trade.exit_date,
        "left1": trade.left1 or "",
        "left2": trade.left2 or "",
        "left3": trade.left3 or "",
        "left4": trade.left4 or "",
        "left5": trade.left5 or "",
        "left6": trade.left6 or "",
        "right1": trade.right1 or "",
        "right2": trade.right2 or "",
        "right3": trade.right3 or "",
        "right4": trade.right4 or "",
        "right5": trade.right5 or "",
        "right6": trade.right6 or "",
        "bottomQ": trade.bottomQ or "",
        "do_follow_plan": trade.do_follow_plan or False,
        "images": image_list
    }
    return jsonify(data)

@app.route('/api/trades', methods=['POST'])
def create_trade():
    data = request.json
    t = Trade(
        symbol=data.get('symbol', ''),
        entry_date=data.get('entry_date', ''),
        exit_date=data.get('exit_date', ''),
        left1=data.get('left1', ''),
        left2=data.get('left2', ''),
        left3=data.get('left3', ''),
        left4=data.get('left4', ''),
        left5=data.get('left5', ''),
        left6=data.get('left6', ''),
        right1=data.get('right1', ''),
        right2=data.get('right2', ''),
        right3=data.get('right3', ''),
        right4=data.get('right4', ''),
        right5=data.get('right5', ''),
        right6=data.get('right6', ''),
        bottomQ=data.get('bottomQ', ''),
        do_follow_plan=data.get('do_follow_plan', False)
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({"id": t.id}), 201

@app.route('/api/trades/<int:trade_id>', methods=['PUT'])
def update_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    data = request.json

    trade.symbol = data.get('symbol', trade.symbol)
    trade.entry_date = data.get('entry_date', trade.entry_date)
    trade.exit_date = data.get('exit_date', trade.exit_date)
    trade.left1 = data.get('left1', trade.left1)
    trade.left2 = data.get('left2', trade.left2)
    trade.left3 = data.get('left3', trade.left3)
    trade.left4 = data.get('left4', trade.left4)
    trade.left5 = data.get('left5', trade.left5)
    trade.left6 = data.get('left6', trade.left6)
    trade.right1 = data.get('right1', trade.right1)
    trade.right2 = data.get('right2', trade.right2)
    trade.right3 = data.get('right3', trade.right3)
    trade.right4 = data.get('right4', trade.right4)
    trade.right5 = data.get('right5', trade.right5)
    trade.right6 = data.get('right6', trade.right6)
    trade.bottomQ = data.get('bottomQ', trade.bottomQ)
    trade.do_follow_plan = data.get('do_follow_plan', trade.do_follow_plan)

    db.session.commit()
    return jsonify({"status": "updated"})

@app.route('/api/trades/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    images = TradeImage.query.filter_by(record_id=trade_id).all()
    for img in images:
        db.session.delete(img)
    db.session.delete(trade)
    db.session.commit()
    return jsonify({"status": "deleted"})

# ------------------------------------------------------------------
# ROUTES - IMAGES
# ------------------------------------------------------------------

@app.route('/api/images', methods=['POST'])
def upload_image():
    record_id = request.form['record_id']
    pane_number = request.form['pane_number']
    image_file = request.files['file']
    blob_data = image_file.read()

    img = TradeImage(
        record_id=record_id,
        pane_number=pane_number,
        blob_data=blob_data
    )
    db.session.add(img)
    db.session.commit()
    return jsonify({"id": img.id}), 201

@app.route('/api/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    img = TradeImage.query.get_or_404(image_id)
    return send_file(
        BytesIO(img.blob_data),
        mimetype='image/png'
    )

@app.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    img = TradeImage.query.get_or_404(image_id)
    db.session.delete(img)
    db.session.commit()
    return jsonify({"status": "deleted"})

# API endpoint to get all tags.
@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.order_by(Tag.name).all()
    data = [{"id": tag.id, "name": tag.name} for tag in tags]
    return jsonify(data)

# API endpoint to add a new tag.
@app.route('/api/tags', methods=['POST'])
def add_tag():
    data = request.get_json()
    tag_name = data.get('name', '').strip()
    if tag_name == '':
        return jsonify({"error": "Tag name cannot be empty."}), 400

    # Check if tag already exists.
    if Tag.query.filter_by(name=tag_name).first():
        return jsonify({"error": "Tag already exists."}), 409

    tag = Tag(name=tag_name)
    db.session.add(tag)
    db.session.commit()
    return jsonify({"id": tag.id, "name": tag.name}), 201

# API endpoint to delete a tag.
@app.route('/api/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return jsonify({"status": "deleted"})

# ------------------------------------------------------------------
# SETUP ENDPOINTS
# ------------------------------------------------------------------

@app.route('/api/setups', methods=['GET'])
def get_all_setups():
    setups = Setup.query.order_by(Setup.id).all()
    data = []
    for s in setups:
        mappings = SetupTagMapping.query.filter_by(setup_id=s.id).all()
        tag_ids = [m.tag_id for m in mappings]
        # For simplicity, assume image navigation: get all images for the setup.
        images = SetupImage.query.filter_by(setup_id=s.id).all()
        image_ids = [img.id for img in images]
        data.append({
            "id": s.id,
            "comment": s.comment or "",
            "image_ids": image_ids,
            "tag_ids": tag_ids
        })
    return jsonify(data)

@app.route('/api/setups/<int:setup_id>', methods=['GET'])
def get_setup(setup_id):
    s = Setup.query.get_or_404(setup_id)
    mappings = SetupTagMapping.query.filter_by(setup_id=s.id).all()
    tag_ids = [m.tag_id for m in mappings]
    images = SetupImage.query.filter_by(setup_id=s.id).all()
    image_ids = [img.id for img in images]
    data = {
        "id": s.id,
        "comment": s.comment or "",
        "image_ids": image_ids,
        "tag_ids": tag_ids
    }
    return jsonify(data)

@app.route('/api/setups', methods=['POST'])
def create_setup():
    data = request.get_json()
    s = Setup(comment=data.get('comment', ''))
    db.session.add(s)
    db.session.commit()
    # Handle tag mapping if provided.
    tag_ids = data.get('tag_ids')
    if tag_ids and isinstance(tag_ids, list):
        for tid in tag_ids:
            mapping = SetupTagMapping(setup_id=s.id, tag_id=tid)
            db.session.add(mapping)
        db.session.commit()
    return jsonify({"id": s.id}), 201

@app.route('/api/setups/<int:setup_id>', methods=['PUT'])
def update_setup(setup_id):
    s = Setup.query.get_or_404(setup_id)
    data = request.get_json()
    s.comment = data.get('comment', s.comment)
    db.session.commit()
    # Update tag mappings: clear existing and add new ones.
    new_tag_ids = data.get('tag_ids')
    if new_tag_ids is not None and isinstance(new_tag_ids, list):
        # Delete existing mappings.
        SetupTagMapping.query.filter_by(setup_id=s.id).delete()
        for tid in new_tag_ids:
            mapping = SetupTagMapping(setup_id=s.id, tag_id=tid)
            db.session.add(mapping)
        db.session.commit()
    return jsonify({"status": "updated"})

@app.route('/api/setups/<int:setup_id>', methods=['DELETE'])
def delete_setup(setup_id):
    s = Setup.query.get_or_404(setup_id)
    # Delete associated images.
    images = SetupImage.query.filter_by(setup_id=s.id).all()
    for img in images:
        db.session.delete(img)
    # Delete associated tag mappings.
    SetupTagMapping.query.filter_by(setup_id=s.id).delete()
    db.session.delete(s)
    db.session.commit()
    return jsonify({"status": "deleted"})

# ------------------------------------------------------------------
# SETUP IMAGE HANDLING
# ------------------------------------------------------------------

@app.route('/api/setup_images', methods=['POST'])
def upload_setup_image():
    setup_id = request.form['setup_id']
    image_file = request.files['file']
    blob_data = image_file.read()
    img = SetupImage(setup_id=setup_id, blob_data=blob_data)
    db.session.add(img)
    db.session.commit()
    return jsonify({"id": img.id}), 201

@app.route('/api/setup_images/<int:image_id>', methods=['GET'])
def get_setup_image(image_id):
    img = SetupImage.query.get_or_404(image_id)
    return send_file(BytesIO(img.blob_data), mimetype='image/png')

@app.route('/api/setup_images/<int:image_id>', methods=['DELETE'])
def delete_setup_image(image_id):
    img = SetupImage.query.get_or_404(image_id)
    db.session.delete(img)
    db.session.commit()
    return jsonify({"status": "deleted"})

import math

@app.route('/api/setups_by_tag')
def setups_by_tag():
    # Get and validate query parameters.
    tag_id = request.args.get('tag_id', type=int)
    if tag_id is None:
        return jsonify({"error": "tag_id is required"}), 400
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 5, type=int)
    
    # Join Setup with SetupTagMapping filtering by tag_id.
    query = db.session.query(Setup).join(SetupTagMapping).filter(SetupTagMapping.tag_id == tag_id).order_by(Setup.id)
    
    total_count = query.count()
    total_pages = math.ceil(total_count / page_size) if page_size else 1

    # Fetch the required page of setups.
    setups = query.offset((page - 1) * page_size).limit(page_size).all()
    
    results = []
    for s in setups:
        # Get all images for this setup.
        images = SetupImage.query.filter_by(setup_id=s.id).all()
        image_ids = [img.id for img in images]
        # Get all tag mappings for this setup.
        mappings = SetupTagMapping.query.filter_by(setup_id=s.id).all()
        tag_ids = [m.tag_id for m in mappings]
        results.append({
            "id": s.id,
            "comment": s.comment or "",
            "image_ids": image_ids,
            "tag_ids": tag_ids
        })
    
    return jsonify({
        "setups": results,
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count
    })


if __name__ == '__main__':
    app.run(debug=True)
