from app import app,db
from datetime import datetime
from sqlalchemy.orm import relationship

class Items(db.Model):
    __tablename__ = 'item'
    Item_ID = db.Column(db.String(80),unique=True, primary_key=True)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    item_desc = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    item_star = db.Column(db.Integer, nullable=False)
    itme_sizes = db.Column(db.String(120),  nullable=True)
    color = db.Column(db.String(120), nullable=False)
    pic = db.Column(db.Text) 

    def __repr__(self):
        return f"<Products(Item_ID='{self.Item_ID}', name='{self.name}',price ='{self.price},category ='{self.category})>"

class Deals(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(80), db.ForeignKey('item.Item_ID'), nullable=False)
    deal = db.Column(db.String(255), nullable=False)
    
    item = relationship('Items', backref='deals')
    def __repr__(self):
        return f"<Deals(id='{self.id}', item_id='{self.item_id}', deal='{self.deal}')>"
    

user_vouchers = db.Table('user_vouchers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('voucher_id', db.Integer, db.ForeignKey('voucher.id'), primary_key=True),
    db.Column('redeemed_on', db.DateTime, default=datetime.utcnow)  # Optional: track when the voucher was redeemed
)

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, default=0)

    vouchers = db.relationship('Voucher', secondary=user_vouchers,
                               backref=db.backref('users', lazy='dynamic'))

    friends = relationship(
        'User',
        secondary='friendship',
        primaryjoin=id == Friendship.user_id,
        secondaryjoin=id == Friendship.friend_id,
        backref='friend_of'
    )

    def __repr__(self):
        return f"<User(username='{self.username}', points='{self.points}')>"
    
class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<UserPreference {self.category} for User {self.user_id}>'
    

class RatingReview(db.Model):
    __tablename__ = 'rating_review'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(80), db.ForeignKey('item.Item_ID'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<RatingReview(id='{self.id}', item_id='{self.item_id}', rating='{self.rating}', review='{self.review}')>"

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.String(80), db.ForeignKey('item.Item_ID'), nullable=False)
    item = db.relationship('Items', backref=db.backref('wishlist_items', lazy=True))

    def __repr__(self):
        return f"<Wishlist(user_id='{self.user_id}', item_id='{self.item_id}')>"

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.String(80), db.ForeignKey('item.Item_ID'), nullable=False)
    item = db.relationship('Items', backref=db.backref('cart_items', lazy=True))

    def __repr__(self):
        return f"<Cart(user_id='{self.user_id}', item_id='{self.item_id}')>"
    
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('item_id', db.String(80), db.ForeignKey('item.Item_ID'), primary_key=True)
)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    tracking_level = db.Column(db.String(50), nullable=True)
    items = db.relationship('Items', secondary=order_items,
                            backref=db.backref('orders', lazy='dynamic'))

    def __repr__(self):
        # Fetching item IDs from the associated items
        item_ids = [item.Item_ID for item in self.items]
        return f"<Order(id='{self.id}', user_id='{self.user_id}', items={item_ids})>"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Admin %r>' % self.username






class Voucher(db.Model):
    __tablename__ = 'voucher'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # Bronze, Silver, Gold, Platinum
    discount = db.Column(db.Integer, nullable=False)  # Discount percentage
    points_cost = db.Column(db.Integer, nullable=False)  # Cost in points

    def __repr__(self):
        return f'<Voucher {self.type} - {self.discount}% off>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])