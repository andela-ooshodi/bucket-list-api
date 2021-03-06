'''
Commandline scripting settings
'''
from app import create_app, db
from app.models import User, BucketList, BucketItem
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


# function registers the application and database instances
# and the models so that they are automatically imported into the shell
def make_shell_context():
    return dict(
        app=app, db=db, User=User,
        BucketList=BucketList,
        BucketItem=BucketItem
    )
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
