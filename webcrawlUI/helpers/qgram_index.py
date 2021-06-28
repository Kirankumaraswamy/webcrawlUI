import sys
import time
import pymysql

from webcrawlUI.helpers.ped_python import ped
from django.conf import settings


# Comment to use C version of prefix edit distance calculation


class QGramIndex:
    """
    A QGram-Index.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if QGramIndex.__instance == None:
            QGramIndex(3)
        return QGramIndex.__instance

    def __init__(self, q):
        '''
        Creates an empty qgram index.
        '''
        if QGramIndex.__instance == None:
            self.q = q
            self.inverted_lists = {}  # The inverted lists
            self.padding = "$" * (q - 1)
            self.wiki_data = []
            self.merge_counter = 0
            self.ped_counter = 0
            QGramIndex.__instance = self
        else:
            raise Exception("This class is a singleton!")

    def build(self):
        '''
        Builds the index from the given file (one line per entity, see ES5).

        The entity IDs are one-based (starting with one).

        The test expects the index to store tuples (<entity id>, <frequency>),
        for each q-gram, where <entity id> is the ID of the entity the
        q-gram appears in, and <frequency> is the number of times it appears
        in the entity.

        For example, the 3-gram "rei" appears 1 time in entity 1 ("frei") and
        one time in entity 2 ("brei"), so its inverted list is
        [(1, 1), (2, 1)].'''
        connection = None
        HOST = settings.DATABASES['default']['HOST']
        USER = settings.DATABASES['default']['USER']
        PASSWORD = settings.DATABASES['default']['PASSWORD']
        DATABASE = settings.DATABASES['default']['NAME']
        try:
            connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
            if connection is not None:
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)

                cursor = connection.cursor()
                try:
                    sql = "select * from webcrawl.webcrawlUI_cities;"
                    n_cities = cursor.execute(sql)
                    cities = cursor.fetchall()

                    for entity_id , city in enumerate(cities):
                        entity_name = city[1]
                        entity_name = entity_name.lower()
                        self.wiki_data.append(entity_name)

                        entity_name = self.normalize(entity_name)

                        for qgram in self.compute_qgrams(entity_name):
                            if qgram not in self.inverted_lists:
                                # If qgram is seen for the first time, create new list.
                                self.inverted_lists[qgram] = [(entity_id, 1)]
                            elif self.inverted_lists[qgram][-1][0] == entity_id:
                                self.inverted_lists[qgram][-1] = \
                                    (entity_id,
                                     self.inverted_lists[qgram][-1][1] + 1)
                            else:
                                self.inverted_lists[qgram].append((entity_id, 1))

                except pymysql.err.DatabaseError as e:
                    print("Error while getting cities: ", str(e))
        except:
            print("Error while connecting to MySQL for cities retrieval")
        finally:
            if (connection is not None):
                cursor.close()
                connection.close()
                print("MySQL connection is closed for weblinks retrieval")

        # TODO: add your code

    def normalize(self, word):
        '''
        Normalize the given string (remove non-word characters and lower case).
        '''

        low = word.lower()
        return ''.join([i for i in low if i.isalnum()])

    def compute_qgrams(self, word):
        '''
        Compute q-grams for padded version of given string.
        '''

        padded_string = self.padding + word
        qgrams = []
        for i in range(len(word) + self.q - 3):
            qgrams.append(padded_string[i:i + self.q])
        return qgrams

    def merge_lists(self, lists):
        '''
        Merges the given inverted lists. The tests assume that the
        inverted lists keep count of the entity ID in the list,
        for example, in the first test below, entity 3 appears
        1 time in the first list, and 2 times in the second list.
        After the merge, it occurs 3 times in the merged list.

        '''

        list1 = lists[0]
        list2 = lists[1]
        # initialize length of the itwo lists
        list1_length = len(list1)
        list2_length = len(list2)
        # pointers to parse the two lists
        list1_index = 0
        list2_index = 0
        # create new list to store the union of values
        merge_list = []

        # loop through the list untill one of the list is completely read
        while list1_index < list1_length and list2_index < list2_length:
            # increment list1 counter if the element is smaller
            # else increment list2 counter if it is greater
            # else increment both counters and add the element into new list
            if list1[list1_index][0] < list2[list2_index][0]:
                merge_list.append((list1[list1_index]))
                list1_index += 1
            elif list1[list1_index][0] > list2[list2_index][0]:
                merge_list.append((list2[list2_index]))
                list2_index += 1
            else:
                (merge_list.append((list1[list1_index][0],
                 list1[list1_index][1] + list2[list2_index][1])))
                list1_index += 1
                list2_index += 1

        if list1_index == list1_length:
            while list2_index < list2_length:
                merge_list.append((list2[list2_index]))
                list2_index += 1
        elif list2_index == list2_length:
            while list1_index < list1_length:
                merge_list.append((list1[list1_index]))
                list1_index += 1

        return merge_list

    def find_matches(self, prefix, delta):
        '''
        Finds all entities y with PED(x, y) <= delta for a given integer delta
        and a given (normalized) prefix x.

        The test checks for a list of triples containing the entity ID,
        the PED distance and its score:

        [(entity id, PED, score), ...]

        The entity IDs are one-based (starting with 1).

        '''

        ped_list = []
        union_list = []

        x = self.normalize(prefix)
        qgrams = self.compute_qgrams(x)

        for i in range(len(qgrams)):
            if qgrams[i] in self.inverted_lists:
                self.merge_counter = self.merge_counter + 1
                union_list = (self.merge_lists([union_list,
                              self.inverted_lists[qgrams[i]]]))

        for index in range(len(union_list)):
            x_length = len(x)
            y = (self.normalize(self.wiki_data[union_list[index][0] -
                 1].split("\t")[0]))
            value = x_length - (delta * self.q)
            count = union_list[index][1]

            if count >= value:
                ped1 = ped(x, y, delta)
                self.ped_counter = self.ped_counter + 1

                if ped1 <= delta:
                    ped_list.append((union_list[index][0], ped1))

        matches = self.rank_matches(ped_list)
        cities = []
        for k in range(len(matches)):
            entity_name = self.wiki_data[matches[k][0]]
            cities.append(entity_name)

            if k == 5:
                break

        return cities

    def rank_matches(self, matches):
        '''
        Ranks the given list of (entity id, PED, s), where PED is the PED
        value and s is the popularity score of an entity.

        The test check for a list of triples containing the entity ID,
        the PED distance and its score:

        [(entity id, PED, score), ...]
        '''
        return sorted(matches, key=lambda tup: (tup[1]))


if __name__ == "__main__":
    i = QGramIndex(3)
    i.build()

    while True:
        prefix = input("Enter search word prefix: ").lower()
        prefix = i.normalize(prefix)
        delta = int(len(prefix)/4)
        i.merge_counter = 0
        i.ped_counter = 0
        start_time = time.monotonic()
        match_list = i.rank_matches(i.find_matches(prefix, delta))
        end_time = time.monotonic()
        for k in range(len(match_list)):
            entity_name = i.wiki_data[match_list[k][0] - 1]
            print(entity_name)

            if k == 4:
                break
        print("Executed in %d msecs: " % ((end_time - start_time) * 1000))
        print("Total number of matches: ", len(match_list))
        print("Number of merges: ", i.merge_counter)
        print("PDE runs: ", i.ped_counter)

