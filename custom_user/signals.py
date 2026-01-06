from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.db import transaction
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from restaurants.models import RestaurantBranches, Restaurants
from foods.models import *

User = get_user_model()


@receiver(post_save, sender=User)
def assign_permissions_by_role(sender, instance, created, **kwargs):
    if not instance.is_staff:
        return

    if instance.is_superuser:
        return

    if instance.role == 'restaurant_admin':
        transaction.on_commit(lambda: assign_restaurant_admin_permissions(instance.pk))
    elif instance.role == 'branch_admin':
        transaction.on_commit(lambda: assign_branch_admin_permissions(instance.pk))



def assign_restaurant_admin_permissions(user_pk):
    try:
        user = User.objects.get(pk=user_pk)

        models = [
            User,
            RestaurantBranches,
            Restaurants,
            Food,
            FoodCategory,
            FoodMenuBranch,
            FoodMenuBranchCollection,
        ]

        permissions_to_add = []

        for model in models:
            try:
                content_type = ContentType.objects.get_for_model(model)

                perms = Permission.objects.filter(
                    content_type=content_type,
                    codename__in=[
                        f'view_{model._meta.model_name}',
                        f'add_{model._meta.model_name}',
                        f'change_{model._meta.model_name}',
                        f'delete_{model._meta.model_name}'
                    ]
                )

                permissions_to_add.extend(perms)
            except Exception:
                pass

        if permissions_to_add:
            user.user_permissions.set(permissions_to_add)
            user.refresh_from_db()

    except User.DoesNotExist:
        pass
    except Exception:
        pass


def assign_branch_admin_permissions(user_pk):
    try:
        user = User.objects.get(pk=user_pk)

        models = [
            RestaurantBranches,
            Food,
            FoodCategory,
            FoodMenuBranch,
            FoodMenuBranchCollection,
        ]

        permissions_to_add = []

        for model in models:
            try:
                if model == RestaurantBranches:
                    content_type = ContentType.objects.get_for_model(model)

                    perms = Permission.objects.filter(
                        content_type=content_type,
                        codename__in=[
                            f'view_{model._meta.model_name}',
                            f'change_{model._meta.model_name}',
                        ]
                    )

                    permissions_to_add.extend(perms)
                    print(f"✅ Added {perms.count()} permissions for {model.__name__}")
                else:
                    content_type = ContentType.objects.get_for_model(model)

                    perms = Permission.objects.filter(
                        content_type=content_type,
                        codename__in=[
                            f'view_{model._meta.model_name}',
                            f'add_{model._meta.model_name}',
                            f'delete_{model._meta.model_name}',
                            f'change_{model._meta.model_name}',
                        ]
                    )

                    permissions_to_add.extend(perms)
                    print(f"✅ Added {perms.count()} permissions for {model.__name__}")

            except Exception as e:
                print(f"❌ Error with {model.__name__}: {e}")

        if permissions_to_add:
            user.user_permissions.set(permissions_to_add)
            print(f"✅ Total {len(permissions_to_add)} permissions assigned to {user.email}")
        else:
            print(f"⚠️ No permissions to add for {user.email}")

    except User.DoesNotExist:
        print(f"❌ User with pk={user_pk} not found")
    except Exception as e:
        print(f"❌ Error in assign_branch_admin_permissions: {e}")
