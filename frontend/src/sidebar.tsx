import {
  AbsoluteCenter,
  Box,
  Circle,
  Flex,
  HStack,
  IconButton,
  Link,
  Stack,
  Text,
} from '@chakra-ui/react';
import { Tooltip } from './components/ui/tooltip';
import {
  ExploreGPTIcon,
  NewChatIcon,
  SidebarIcon,
  SmallGPTIcon,
  UpgradeIcon,
} from './icons/sidebar-icons';

import { useSidebarContext } from './sidebar-context';
import { HatIcon, IllustrationIcon } from './icons/other-icons';

export function Sidebar() {
  const { sideBarVisible, toggleSidebar } = useSidebarContext();

  return (
    <Box
      bg='#FFEED6'
      w={!sideBarVisible ? '0' : '260px'}
      overflow='hidden'
      transition=' width 0.3s'
    >
      <Stack h='full' px='3' py='2'>
        <Flex justify='space-between'>
          <Tooltip
            content='Fechar sidebar'
            positioning={{ placement: 'right' }}
            showArrow
          >
            <IconButton variant='ghost' onClick={toggleSidebar} _hover={{ bg: '#ecad89' }}>
              <SidebarIcon fontSize='2xl' color='#E3661D' />
            </IconButton>
          </Tooltip>

          <Tooltip content='Novo chat' showArrow>
            <IconButton variant='ghost' _hover={{ bg: '#ecad89' }}>
              <NewChatIcon fontSize='2xl' color='#E3661D' />
            </IconButton>
          </Tooltip>
        </Flex>

        <Stack px='2' gap='0' flex='1'>
          <HStack
            position='relative'
            className='group'
            _hover={{
              bg: '#ecad89'
            }}
            px='1'
            h='10'
            borderRadius='lg'
            w='100%'
            whiteSpace='nowrap'
          >
            <Link href='#' variant='plain' _hover={{ textDecor: 'none'}} >
              <Circle size='6' bg='bg' borderWidth='1px'>
                <HatIcon fontSize='md' color="#E3661D" bg="#ffeed6" />
              </Circle>
              <Text fontSize='sm' fontWeight='md' color="#E3661D">
                Apoema GPT
              </Text>
            </Link>
            <AbsoluteCenter
              axis='vertical'
              right='2'
              display='none'
              _groupHover={{ display: 'initial' }}
            >
              <Tooltip
                content='Novo chat'
                positioning={{ placement: 'right' }}
                showArrow
              >
                <NewChatIcon
                  fontSize='md'
                  color='#E3661D'
                  _hover={{ bg: '#ecad89' }}
                />
              </Tooltip>
            </AbsoluteCenter>
          </HStack>

          
        </Stack>

        
      </Stack>
    </Box>
  );
}
