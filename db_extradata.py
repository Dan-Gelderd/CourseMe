#!flask/bin/python
from courseme import db, hash_string
from courseme.models import Module, User, ROLE_USER, ROLE_ADMIN, Objective, Institution, Question
from datetime import datetime

q = Question(
    question =
'''
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

q = Question(
    question =
'''
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
'''
\[  \\begin{aligned}
\\nabla \times \\vec{\mathbf{B}} -\, \\frac1c\, \\frac{\partial\\vec{\mathbf{E}}}{\partial t} &amp; = \\frac{4\pi}{c}\\vec{\mathbf{j}} \\
\\nabla \cdot \\vec{\mathbf{E}} &amp; = 4 \pi \rho \\
\\nabla \times \\vec{\mathbf{E}}\, +\, \\frac1c\, \\frac{\partial\\vec{\mathbf{B}}}{\partial t} &amp; = \\vec{\mathbf{0}} \\
\\nabla \cdot \\vec{\mathbf{B}} &amp; = 0 \end{aligned}
\]
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



