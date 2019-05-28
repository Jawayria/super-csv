# -*- coding: utf-8 -*-
"""
Database models for super_csv.
"""

from __future__ import absolute_import, unicode_literals
import uuid
import six

from crum import get_current_user
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models

from model_utils.models import TimeStampedModel


def csv_class_path(instance, filename):
    return 'csv/{0}/{1}/{2}'.format(instance.class_name, instance.unique_id, filename)


class CSVOperation(TimeStampedModel):
    class_name = models.CharField(max_length=255, db_index=True)
    unique_id = models.CharField(max_length=255, db_index=True)
    operation = models.CharField(max_length=255)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    data = models.FileField(upload_to=csv_class_path, max_length=255)

    @classmethod
    def _get_class_name(cls, obj):
        if not isinstance(obj, six.string_types):
            obj = '%s.%s' % (obj.__class__.__module__, obj.__class__.__name__)
        return obj

    @classmethod
    def get_latest(cls, class_name_or_obj, unique_id):
        try:
            return cls.objects.filter(class_name=cls._get_class_name(class_name_or_obj), unique_id=unique_id).order_by('-modified')[0]
        except IndexError:
            return None

    @classmethod
    def record_operation(cls, class_name_or_obj, unique_id, operation, data):
        instance = cls(class_name=cls._get_class_name(class_name_or_obj), unique_id=unique_id, operation=operation)
        instance.user = get_current_user()
        instance.data.save(uuid.uuid4(), ContentFile(data))
        return instance

    def __str__(self):
        return 'Operation for {} {}'.format(self.class_name, self.unique_id)