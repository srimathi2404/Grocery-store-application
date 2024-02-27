from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
import hashlib
db = SQLAlchemy()

class Users(db.Model,UserMixin):
    __tablename__='user_details'
    username=db.Column(db.String,primary_key=True)
    password=db.Column(db.String,nullable=False)
    first_name=db.Column(db.String,nullable=False)
    last_name=db.Column(db.String,nullable=False)
    email=db.Column(db.String,unique=True, nullable=False)
    mobile_no=db.Column(db.Integer,unique=True, nullable=False)
    purchase=db.Column(db.Integer)
    authenticated=db.Column(db.Integer)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean())
    roles = db.relationship('role', secondary='role_users',
                         backref=db.backref('users', lazy='dynamic'))
    
    @property
    def is_authorised(self):
        return self.authenticated
    
    @property
    def get_roles(self):
        return [role.name for role in self.roles]
    
    def __repr__(self):
        return '<User %r>' % self.email

def get_pend_manager():
    x=db.session.query(Users).filter(Users.active==False).all()
    l=[]
    for i in x:
        l.append(i.username)
    return l
def approve_managers(username):
    x=db.session.query(Users).filter(Users.username==username).first()
    x.active=True
    db.session.commit()


class role(db.Model,RoleMixin):
    __tablename__="role"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String,nullable=True,unique=True)
    description = db.Column(db.String(255))

class RolesUsers(db.Model):
    __tablename__ = 'role_users'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey('user_details.username'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class logs(db.Model):
    __tablename__='logs'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String,db.ForeignKey('user_details.username'),nullable=False)
    timestamp=db.Column(db.String)

class sections(db.Model):
    __tablename__='section_details'
    section_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    section_name=db.Column(db.JSON,nullable=False,unique=True)
    is_approve=db.Column(db.Integer,nullable=False)
def sec_unapprove():
    x=db.session.query(sections).filter(sections.is_approve.in_([0,-1,-2])).all()
    return x

def all_sec():
    y=db.session.query(sections).filter(sections.is_approve.in_([1,-1,-2])).all()
    return y
def get_sec(id):
    x=db.session.query(sections).filter(sections.section_id==id).first()
    return x
def add_section(name,ia):
    x=sections(section_name=name,is_approve=ia)
    db.session.add(x)
    db.session.commit()
def edit_sec(id,name,is_approve):
    sec=db.session.query(sections).filter(sections.section_id==id).first()
    sec.section_name=name
    sec.is_approve=is_approve
    db.session.commit()
def edit_sec_isapprove(id,is_approve):
    sec=db.session.query(sections).filter(sections.section_id==id).first()
    sec.is_approve=is_approve
    db.session.commit()
def del_sec(id):
    sec=db.session.query(sections).filter(sections.section_id==id).first()
    pro=db.session.query(products).filter(products.section_id==id).all()
    if sec:
        x=sec.section_name
        db.session.delete(sec)
        for i in pro:
            db.session.delete(i)
        db.session.commit()
        return "section deleted"+x['new_name']
    return "error"

class products(db.Model):
    __tablename__='product_details'
    product_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    product_name=db.Column(db.String,nullable=False,unique=True)
    manufacture_date=db.Column(db.String)
    expiry_date=db.Column(db.String)
    price=db.Column(db.Integer)
    instock_quantity=db.Column(db.Integer)
    section_id=db.Column(db.Integer,db.ForeignKey('section_details.section_id'))
    unit=db.Column(db.String,nullable=False)
    #section=db.relationship('section_details')

def all_prod():
    prod=db.session.query(products).all()
    return prod
def add_prod(n,m,e,p,q,sec,u):
    x=products(product_name=n,manufacture_date=m,expiry_date=e,price=p,instock_quantity=q, section_id=sec,unit=u)
    db.session.add(x)
    db.session.commit()
def get_prod(prod_id):
    x=db.session.query(products).filter(products.product_id==prod_id).first()
    if x:
        return x

def get_prod_of_sec(sec_id):
    pro=db.session.query(products).filter(products.section_id==sec_id).all()
    return pro
def edit_pro(id,n,m,e,p,q,u):
    pro=db.session.query(products).filter(products.product_id==id).first()
    pro.product_name=n
    pro.manufacture_date=m
    pro.expiry_date=e
    pro.price=p
    pro.instock_quantity=q
    pro.unit=u
    db.session.commit()
def del_pro(id):
    pro=db.session.query(products).filter(products.product_id==id).first()
    db.session.delete(pro)
    db.session.commit()


    
class Cart(db.Model):
    __tablename__='Cart'
    cart_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String,db.ForeignKey('user_details.username'))
    product_id=db.Column(db.Integer,db.ForeignKey('product_details.product_id'))
   
    quantity=db.Column(db.Integer)

    def del_cart(username):
        car=Cart.query.filter_by(username=username).all()
        for i in car:
            db.session.delete(i)
        db.session.commit()
    def add_cart(username,pid,quantity):
        check_exist=Cart.query.filter_by(product_id=pid).first()
        if check_exist!=None:
             check_exist.quantity=int(check_exist.quantity)+int(q)
        else:
            x=Cart(username=username,product_id=pid,quantity=quantity)
            db.session.add(x)
            db.session.commit()
        
        i=products.query.filter_by(product_id=pid).first()
        i.instock_quantity=int(i.instock_quantity)-int(quantity)
        db.session.commit()
def update_quantity(username,id,q):
    x=db.session.query(Cart).filter(Cart.username==username,Cart.product_id==id).first()
    x.quantity+=q
    db.session.commit()

class purchases(db.Model):
    __tablename__='user_purchase'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    purchase_id=db.Column(db.Integer,nullable=False)
    username=db.Column(db.String,db.ForeignKey('user_details.username'))
    product_id=db.Column(db.Integer,db.ForeignKey('product_details.product_id'))
    product_name=db.Column(db.String,db.ForeignKey('product_details.product_name'))
    section_id=db.Column(db.Integer,db.ForeignKey('section_details.section_id'))
    price=db.Column(db.Integer,db.ForeignKey('product_details.price'))
    quantity=db.Column(db.Integer)
    amount=db.Column(db.Integer)

    def add_purchase(username,pid,pname,sid,price,quantity,purid,amt):
        u=purchases(purchase_id=purid,username=username,product_id=pid,product_name=pname,section_id=sid,price=price,quantity=quantity,amount=amt)
        db.session.add(u)
        
        db.session.commit()
