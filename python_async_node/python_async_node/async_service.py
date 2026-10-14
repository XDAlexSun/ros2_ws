import asyncio

from example_interfaces.srv import Trigger
import rclpy
from rclpy.experimental import AsyncNode


class TriggerServer(AsyncNode):

    def __init__(self):
        super().__init__('trigger_server')
        self._service = self.create_service(
            Trigger, 'trigger', self._callback
        )

    async def _callback(self, _request, response):
        self.get_logger().info('Incoming trigger request')
        await self.get_clock().sleep(2.0)
        response.success = True
        response.message = 'Slept for 2.0s'
        return response


async def _async_main():
    with rclpy.init():
        node = TriggerServer()
        await node.run()


def main():
    asyncio.run(_async_main())


if __name__ == '__main__':
    main()