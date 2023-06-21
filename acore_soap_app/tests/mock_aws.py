# -*- coding: utf-8 -*-

import typing as T
from boto_session_manager import BotoSesManager


class BaseMockTest:
    """
    Simple base class for mocking AWS services.

    Usage::

        import moto

        class Test(BaseMockTest):
            mock_list = [
                moto.mock_s3,
            ]

            @classmethod
            def setup_class_post_hook(cls):
                cls.bsm.s3_client.create_bucket(Bucket="my-bucket")
                cls.bsm.s3_client.put_object(
                    Bucket="my-bucket",
                    Key="file.txt",
                    Body="hello world",
                )

            def test(self):
                assert (
                    self.bsm.s3_client.get_object(Bucket="my-bucket", Key="file.txt")["Body"]
                    .read()
                    .decode("utf-8")
                    == "hello world"
                )

    """
    use_mock: bool = True
    region_name: str = "us-east-1"
    mock_list: list = []

    # Don't overwrite the following
    bsm: T.Optional[BotoSesManager] = None
    _mock_list: list = []

    @classmethod
    def setup_moto(cls):
        if cls.use_mock:
            for mock_abc in cls.mock_list:
                mocker = mock_abc()
                mocker.start()
                cls._mock_list.append(mocker)
        cls.bsm = BotoSesManager(region_name=cls.region_name)

    @classmethod
    def teardown_moto(cls):
        if cls.use_mock:
            for mocker in cls._mock_list:
                mocker.stop()

    @classmethod
    def setup_class_pre_hook(cls):  # pragma: no cover
        pass

    @classmethod
    def setup_class_post_hook(cls):  # pragma: no cover
        pass

    @classmethod
    def setup_class(cls):
        cls.setup_class_pre_hook()
        cls.setup_moto()
        cls.setup_class_post_hook()

    @classmethod
    def teardown_class_pre_hook(cls):  # pragma: no cover
        pass

    @classmethod
    def teardown_class_post_hook(cls):  # pragma: no cover
        pass

    @classmethod
    def teardown_class(cls):
        cls.teardown_class_pre_hook()
        cls.teardown_moto()
        cls.teardown_class_post_hook()
