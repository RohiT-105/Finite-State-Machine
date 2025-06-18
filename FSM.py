from transitions import Machine

class RegexFSM(object):
    def __init__(self, pattern):
        self.pattern = pattern
        self.matches = []
        self.current_match = []
        self.current_index = 0
        self.machine = Machine(model=self, states=['start'], initial='start', auto_transitions=False, send_event=True)
        self.is_simple_pattern = not any(char in pattern for char in '*+|.')
        if not self.is_simple_pattern:
            self._build_fsm()

    def _build_fsm(self):
        current_state = 'start'
        i = 0
        while i < len(self.pattern):
            char = self.pattern[i]
            next_state = f'matching_{char}_{i}'
            self.machine.add_states([next_state])

            if i + 1 < len(self.pattern) and self.pattern[i + 1] in '*+':
                modifier = self.pattern[i + 1]
                trigger_event = 'read_any' if char == '.' else f'read_{char}'
                self.machine.add_transition(trigger=trigger_event, source=current_state, dest=next_state,
                                            after='on_match')
                self.machine.add_transition(trigger=trigger_event, source=next_state, dest=next_state, after='on_match')
                self.machine.add_transition(trigger='skip', source=current_state, dest=next_state, after='skip_char')
                i += 1
            else:
                trigger_event = 'read_any' if char == '.' else f'read_{char}'
                self.machine.add_transition(trigger=trigger_event, source=current_state, dest=next_state,
                                            after='on_match')

            current_state = next_state
            i += 1

        self.machine.add_transition(trigger='finish', source='*', dest='start', after='save_match')

    def on_match(self, event):
        char = event.kwargs.get('char', '')
        self.current_match.append((self.current_index, char))

    def save_match(self, event):
        if self.current_match:
            start_index = self.current_match[0][0]
            end_index = self.current_match[-1][0] + 1
            self.matches.append((start_index, end_index))
            self.current_match = []

    def skip_char(self, event):
        pass

    def process_string(self, input_string):
        if self.is_simple_pattern:
            RED = '\033[94m'
            RESET = '\033[0m'
            print(input_string.replace(self.pattern, f"{RED}{self.pattern}{RESET}"))
        else:
            self.current_index = 0
            while self.current_index < len(input_string):
                char = input_string[self.current_index]
                triggers = self.machine.get_triggers(self.state)
                if 'read_any' in triggers:
                    self.read_any(char=char)
                elif f'read_{char}' in triggers:
                    getattr(self, f'read_{char}')(char=char)
                elif 'skip' in triggers:
                    self.skip()
                elif 'finish' in triggers:
                    self.finish()

                if self.state == 'start' and self.current_match:
                    self.save_match(None)

                self.current_index += 1

            if self.current_match:
                self.save_match(None)

            print(self.get_highlighted_text(input_string))

    def get_highlighted_text(self, input_string):
        result = []
        last_index = 0
        for start, end in self.matches:
            result.append(input_string[last_index:start])
            result.append(f'\033[94m{input_string[start:end]}\033[0m')
            last_index = end
        result.append(input_string[last_index:])
        return ''.join(result)


testcases = int(input("Input number of test cases: "))
for i in range(testcases):
    pattern = input("Input regex string: ")
    fsm = RegexFSM(pattern)
    test_string = input("Input sample string: ")
    fsm.process_string(test_string)
