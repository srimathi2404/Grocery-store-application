from flask_restful import Resource, Api, marshal, reqparse, fields, marshal_with
from caching import cache
from flask import abort, jsonify, request
from flask_security import SQLAlchemySessionUserDatastore, Security, login_user, logout_user
from flask_security import current_user, auth_required, login_required, roles_required, roles_accepted,login_user, logout_user,auth_token_required
api = Api(prefix='/api')
from models import sec_unapprove,all_sec,get_sec,edit_sec,edit_sec_isapprove,all_prod,del_sec,add_prod,get_prod_of_sec,get_prod,edit_pro,del_pro,db,sections,products,add_section,add_cart,del_cart,Cart,update_quantity

###  ADMIN FUNCTION #####

#ADD SECTION
sec=reqparse.RequestParser()
sec.add_argument('old_name')
sec.add_argument('new_name')
sec.add_argument('is_approve')

#UPDATE SECTION


section_update= reqparse.RequestParser()
section_update.add_argument('old_name')
section_update.add_argument('new_name')
section_update.add_argument('is_approve')

section_to_approve= reqparse.RequestParser()
section_to_approve.add_argument('is_approve')

sec_name= reqparse.RequestParser()
sec_name.add_argument('old_name')
sec_name.add_argument('new_name')

SECTION_NAME={
    "old_name": fields.String,
    "new_name": fields.String
} 

SECTION_ALL = {
    'section_name': fields.List(fields.Nested(SECTION_NAME)),
    'section_id': fields.Integer,
    'is_approve': fields.Integer
}
SECTION_IS_APPROVE={
    'is_approve': fields.Integer
}
class pending_sec(Resource):
    def get(self):
        pending=sec_unapprove()
        return jsonify(marshal(pending,SECTION_ALL))
    
class add_sec(Resource):
    @cache.cached(timeout=15)
    def get(self):
        sec=all_sec()
        

        return jsonify(marshal(sec,SECTION_ALL))
    @auth_required('token')
    # @roles_accepted('admin', 'manager')
    def post(self):
        data=sec.parse_args()
        x=data['old_name']
        y=data['new_name']
        z=data['is_approve']
        name={
            'old_name':x,
            'new_name':y
        }
        
        # if z=='1':
        add_section(name,z)
        return jsonify({"message":"section added"})
        # else:
        #     return jsonify({'message':'error'})
class sec_update_del(Resource):
    @marshal_with(SECTION_ALL)
    @auth_required('token')
    def get(self,id):
        x=get_sec(int(id))
     

        return marshal(x,SECTION_ALL)
   
    @auth_required('token')
    # @roles_accepted('admin','manager')
    def put(self,id):
        data=section_update.parse_args()
        x=data['old_name']
        y=data['new_name']
        name={'old_name':x,'new_name':y}
        z=data['is_approve']
        flag=db.session.query(sections).filter(sections.section_id==id).first()
        if flag:
            edit_sec(id,name,int(z))
            return jsonify({"message":"section name changed from  "+x+"  to  "+y})
        else:
            return "error"
        
    # @marshal_with(SECTION_IS_APPROVE)
    @auth_required('token')
    @roles_required('admin')
    def patch(self,id):
        data=section_to_approve.parse_args()
        x=data['is_approve']
        flag=db.session.query(sections).filter(sections.section_id==id).first()
        if flag:
            edit_sec_isapprove(id,x)
            return jsonify({"message":"section ia edited"})
        else:
            return "error"
    # @auth_required('token')
    # @roles_accepted('admin', 'manager')
    def delete(self, id):
        flag=db.session.query(sections).filter(sections.section_id==id).first()
        if flag:
            x=del_sec(id)
            return jsonify({"message":x})
        else:
            return "error"

    



pro=reqparse.RequestParser()
pro.add_argument('product_name')
pro.add_argument('manufacture_date')
pro.add_argument('expiry_date')
pro.add_argument('price')
pro.add_argument('instock_quantity')
# pro.add_argument('sec_id')
pro.add_argument('unit')

PRODUCT_ALL={'product_id':fields.Integer,
             'product_name':fields.String,
             'manufacture_date':fields.String,
             'expiry_date':fields.String,
             'price':fields.Integer,
             'instock_quantity':fields.Integer,
             'section_id':fields.Integer,
             'unit':fields.String}

class all_prod(Resource):
    
    def get(self):
        return marshal(all_prod(),PRODUCT_ALL)
class prod_of_one_sec(Resource):
    @cache.cached(timeout=15)
    def get(self,sec_id):
        return marshal(get_prod_of_sec(sec_id),PRODUCT_ALL)
    @auth_required('token')
    @roles_accepted('manager','admin')
    def post(self, sec_id):
        data=pro.parse_args()
        n=data['product_name']
        m=data['manufacture_date']
        e=data['expiry_date']
        p=data['price']
        q=data['instock_quantity']
        u=data['unit']
        flag=db.session.query(sections).filter(sections.section_id==sec_id).first()
        if flag:
            add_prod(n,m,e,p,q,sec_id,u)
            return jsonify({"message":"product added"})

        else:
            return "error"
class prod_update_del(Resource):
    
    def get(self,prod_id):
        return marshal(get_prod(prod_id),PRODUCT_ALL)
    def put(self,prod_id):
        data=pro.parse_args()
        name=data['product_name']
        mdate=data['manufacture_date']
        edate=data['expiry_date']
        p=data['price']
        q=data['instock_quantity']
        u=data['unit']
        flag=db.session.query(products).filter(products.product_id==prod_id).first()
        if flag:
            edit_pro(prod_id,name,mdate,edate,p,q,u)
            return jsonify({"message":"product edited"})
        else:
            return "error"
    def delete(self,prod_id):
        flag=db.session.query(products).filter(products.product_id==prod_id).first()
        if flag:
            del_pro(prod_id)
            return jsonify({"message":"product deleted"})
        else:
            return "error"
CART={'username':fields.String,'product_id':fields.String,'quantity':fields.Integer}
cart_data=reqparse.RequestParser()
cart_data.add_argument("product_id")

cart_quantity=reqparse.RequestParser()
cart_quantity.add_argument('quantity')
class cart(Resource):
    @auth_required('token')
    @roles_accepted('user')
    def post(self):
        username=current_user.id
        args=cart_data.parse_args()
        pid=args['product_id']
        quantity=args['quantity']
        return marshal(add_cart(username,pid,quantity))
    @auth_required('token')
    @roles_accepted('user')
    def get(self):
        username=current_user.user_id
        items=db.session.query(Cart).filter(Cart.username==username).all()
        pro_list=[]
        for item in items:
            pro=db.session.query(products).filter(products.product_id==items.product_id).first()
            if pro:
                pro_data={'product_id':item.product_id,'username':item.username,'product_name':pro.product_name,'manufacture_date':pro.manufacture_date,'expiry_date':pro.expiry_date,'price':pro.price,'quantity':Cart.quantity}
                pro_list.append(pro_data)
        return pro_list
class cartCRUD(Resource):
    def delete(self,prod_id):
        username=current_user.username
        del_cart(username)
        return jsonify({"message":"cart deleted"})
    def put(self,prod_id):
        username=current_user.username
        data=cart_quantity.parse_args()
        q=data['quantity']
        update_quantity(username,prod_id,q)
  

    


   
    
api.add_resource(pending_sec,'/pending_sec')
api.add_resource(add_sec,'/sections')
api.add_resource(sec_update_del,'/sections/<id>')
api.add_resource(all_prod,'/products')
api.add_resource(prod_of_one_sec,'/products/<sec_id>')
api.add_resource(prod_update_del,'/sections/products/<prod_id>')
api.add_resource(cart,'/cart')
api.add_resource(cartCRUD,'/cart/<prod_id>')




