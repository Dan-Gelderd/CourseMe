#!flask/bin/python
from courseme import db, hash_string
from courseme.models import Module, User, ROLE_USER, ROLE_ADMIN, Objective, Institution, Question
from datetime import datetime


q = Question(
    question =
r'''
Finally, while display equations look good for a page of samples, the ability to mix math and text in a paragraph is also important. This expression \(\sqrt{3x-1}+(1+x)^2\) is an example of an inline equation.  As you see, MathJax equations can be used this way as well, without unduly disturbing the spacing between lines.
''',
    
    answer = "",
    time_created = datetime.utcnow(),
    last_updated = datetime.utcnow(),
    locked = datetime.utcnow(),
    extension = False,
    author_id = User.main_admin_user().id,
    objective_id = 1
)

db.session.add(q)

q = Question(
    question =
r'''
\begin{aligned}
\nabla \times \vec{\mathbf{B}} -\, \frac1c\, \frac{\partial\vec{\mathbf{E}}}{\partial t} & = \frac{4\pi}{c}\vec{\mathbf{j}} \\   \nabla \cdot \vec{\mathbf{E}} & = 4 \pi \rho \\
\nabla \times \vec{\mathbf{E}}\, +\, \frac1c\, \frac{\partial\vec{\mathbf{B}}}{\partial t} & = \vec{\mathbf{0}} \\
\nabla \cdot \vec{\mathbf{B}} & = 0 \end{aligned}

''',
    
    answer = "",
    time_created = datetime.utcnow(),
    last_updated = datetime.utcnow(),
    locked = datetime.utcnow(),
    extension = False,
    author_id = User.main_admin_user().id,
    objective_id = 1
)


db.session.add(q)


q = Question(
    question =
r'''
\[ \frac{1}{\Bigl(\sqrt{\phi \sqrt{5}}-\phi\Bigr) e^{\frac25 \pi}} =
1+\frac{e^{-2\pi}} {1+\frac{e^{-4\pi}} {1+\frac{e^{-6\pi}}
{1+\frac{e^{-8\pi}} {1+\ldots} } } } \]
''',
    
    answer = "",
    time_created = datetime.utcnow(),
    last_updated = datetime.utcnow(),
    locked = datetime.utcnow(),
    extension = False,
    author_id = User.main_admin_user().id,
    objective_id = 1
)


db.session.add(q)

db.session.commit()


q = Question(
    question =
r'''
\[\mathbf{V}_1 \times \mathbf{V}_2 =  \begin{vmatrix}
\mathbf{i} & \mathbf{j} & \mathbf{k} \\
\frac{\partial X}{\partial u} &  \frac{\partial Y}{\partial u} & 0 \\
\frac{\partial X}{\partial v} &  \frac{\partial Y}{\partial v} & 0
\end{vmatrix}  \]
''',
    
    answer = "",
    time_created = datetime.utcnow(),
    last_updated = datetime.utcnow(),
    locked = datetime.utcnow(),
    extension = False,
    author_id = User.main_admin_user().id,
    objective_id = 1
)


db.session.add(q)

db.session.commit()


q = Question(
    question =
r'''
\[  1 +  \frac{q^2}{(1-q)}+\frac{q^6}{(1-q)(1-q^2)}+\cdots =
\prod_{j=0}^{\infty}\frac{1}{(1-q^{5j+2})(1-q^{5j+3})},
\quad\quad \text{for $|q|<1$}. \]
''',
    
    answer = "",
    time_created = datetime.utcnow(),
    last_updated = datetime.utcnow(),
    locked = datetime.utcnow(),
    extension = False,
    author_id = User.main_admin_user().id,
    objective_id = 1
)


db.session.add(q)

db.session.commit()



q = Question(
    question =
r'''
This is a question:
\[  1 +  \frac{q^2}{(1-q)}+\frac{q^6}{(1-q)(1-q^2)}+\cdots =
\prod_{j=0}^{\infty}\frac{1}{(1-q^{5j+2})(1-q^{5j+3})},
\quad\quad \text{for $|q|<1$}. \]

And here is the answer \(\sqrt{3x-1}+(1+x)^2\).
Isn't it great.
''',
    
    answer = "",
    time_created = datetime.utcnow(),
    last_updated = datetime.utcnow(),
    locked = datetime.utcnow(),
    extension = False,
    author_id = User.main_admin_user().id,
    objective_id = 1
)


db.session.add(q)

db.session.commit()