import { Button } from '@/components/ui/button';
import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuSeparator,
  MenuTrigger,
} from '@/components/ui/menu';
import { Box, Circle, HStack, Stack, Text } from '@chakra-ui/react';
import {
  ChatGPTMenuIcon,
  ChatGPTPlusIcon,
  CheckIcon,
  MenuIcon,
  TemporaryChatIcon,
} from './icons/other-icons';
import { Switch } from './components/ui/switch';

interface MenuItemDetailProps {
  icon: React.ReactElement;
  title: string;
  description?: string;
  element?: React.ReactElement;
}

function MenuItemDetail(props: MenuItemDetailProps) {
  const { icon, title, description, element, ...rest } = props;
  return (
    <HStack w='100%' {...rest}>
      <Circle size='8' bg='#e3661d'>
        {icon}
      </Circle>
      <Stack gap='0' flex='1'>
        <Text color="#e3661d">{title}</Text>
        <Text fontSize='xs' color='#e3661d'>
          {description}
        </Text>
      </Stack>
      <Box>{element}</Box>
    </HStack>
  );
}

export const ApoemaGPTMenu = () => {
  return (
    <MenuRoot >
      <MenuTrigger asChild >
        <Button
          variant='ghost'
          fontSize='lg'
          fontWeight='bold'
          color='#FFEED6'
          _hover={{ bg: '#ecad89' }}
        >
          Apoema GPT <MenuIcon />
        </Button>
      </MenuTrigger>
      <MenuContent minW='320px' borderRadius='2xl' bg="#ffeed6">
        <MenuItem value='chatgpt-plus' py='2'>
          <MenuItemDetail
            title='Editais de fomento'
            icon={<ChatGPTPlusIcon color="#f4f4f5" />}
            description='Encontre editais de fomento para o seu projeto'   
          />
        </MenuItem>

        <MenuItem value='chatgpt' py='2'>
          <MenuItemDetail
            title='Link 1'
            icon={<ChatGPTMenuIcon  color="#f4f4f5" />}
            description='Lorem ipsum'
            element={<CheckIcon fontSize='lg' />}
          />
        </MenuItem>

        <MenuSeparator />
        <MenuItem value='temporary-chat' py='2'>
          <MenuItemDetail
            title='Link 2'
            icon={<TemporaryChatIcon  color="#f4f4f5"/>}
            element={<Switch size='sm' />}
          />
        </MenuItem>
      </MenuContent>
    </MenuRoot>
  );
};
