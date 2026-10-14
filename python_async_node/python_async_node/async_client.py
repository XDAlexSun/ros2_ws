import asyncio

from example_interfaces.srv import Trigger
import rclpy
from rclpy.experimental import AsyncNode


async def _async_main():
    with rclpy.init():
        async with AsyncNode('trigger_client') as node:
            client = node.create_client(Trigger, 'trigger')

            node.get_logger().info('Waiting for trigger service...')
            await client.wait_for_service()
            node.get_logger().info('Service is available, sending request')

            request = Trigger.Request()
            response = await client.call(request)

            node.get_logger().info(
                f'Service responded: success={response.success}, '
                f'message="{response.message}"'
            )


def main():
    asyncio.run(_async_main())


if __name__ == '__main__':
    main()