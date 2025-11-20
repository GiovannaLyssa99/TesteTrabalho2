import { Flex, IconButton } from '@chakra-ui/react';
import { ApoemaGPTMenu } from './ApoemaGPTMenu';
import { Avatar } from './components/ui/avatar';
import { Tooltip } from './components/ui/tooltip';
import { NewChatIcon, SidebarIcon } from './icons/sidebar-icons';
import { useSidebarContext } from './sidebar-context';

export function TopSection() {
  const { sideBarVisible, toggleSidebar } = useSidebarContext();
  return (
    <Flex justify='space-between' align='center' p='2' bg="#E3661D"> 
      {!sideBarVisible && (
        <Flex>
          <Tooltip
            content='Close sidebar'
            positioning={{ placement: 'right' }}
            showArrow
          >
            <IconButton variant='ghost' onClick={toggleSidebar} _hover={{ bg: '#ecad89' }}>
              <SidebarIcon fontSize='2xl' color='#ffeed6' />
            </IconButton>
          </Tooltip>

          <Tooltip content='New chat' showArrow>
            <IconButton variant='ghost' _hover={{ bg: '#ecad89' }}>
              <NewChatIcon fontSize='2xl' color='#ffeed6' />
            </IconButton>
          </Tooltip>
          <ApoemaGPTMenu />
        </Flex>
      )}
      {sideBarVisible && <ApoemaGPTMenu />}

      <Avatar
        name='Esther'
        size='sm'
        colorPalette='teal'
        variant='solid'
        mr='3'
      />
    </Flex>
  );
}
