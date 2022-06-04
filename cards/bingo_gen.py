import random
style = '''<style>
  .card {
    background-color: #FC94aF;
    /* background-color: #446444; */
    /* background-image: url("background.webp"); */
    border-radius: 10px;
    padding: 10px;
    margin: 40px;
  }
  .headers {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
  }
  .headers > div {
    text-align: center;
  }

  .headers > div {
    font-size: 42px;
    color: #fff;
    font-weight: bold;
  }
  .bingo-body {
    display: grid;
    grid-template-rows: 1fr 1fr 1fr 1fr 1fr;
    grid-auto-flow: column;
  }
  .number {
    padding: 20px 0;
    border: 1px solid #000;
    background-color: #fff;
    text-align: center;
    position: relative;
    color: #000;
    font-size: 50px;
  }

  .img-container {
    position: absolute;
    top: 10px;
    bottom: 10px;
    left: 0;
    right: 0;
  }
  img {
    object-fit: contain;
    height: 100%;
    width: 100%;
  }

  @media print {
    .card {
      break-inside: avoid;
    }
  }
</style>
'''

board = '''<div class="card">
  <div class="headers">
    <div><span>B</span></div>
    <div><span>I</span></div>
    <div><span>N</span></div>
    <div><span>G</span></div>
    <div><span>O</span></div>
  </div>
  <div class="bingo-body">
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number"><div class="img-container"><img src="hearts.png"></div></div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
    <div class="number">XXX</div>
  </div>
</div>
'''


def get_board(arr):
    s = board
    for i in arr:
        s = s.replace('XXX', str(i), 1)
    return s


def get_html(boards):
    return style + '\n'.join(boards)


num_boards_to_gen = 220

random.seed(1337)
# all_bingo_numbers = [i+1 for i in range(75)]
bingo_numbers = [[i*15+j+1 for j in range(15)] for i in range(5)]
boards = []
sanitycheck = set()
while len(boards) < num_boards_to_gen:
    arr = random.sample(bingo_numbers[0], k=5) \
        + random.sample(bingo_numbers[1], k=5) \
        + random.sample(bingo_numbers[2], k=4) \
        + random.sample(bingo_numbers[3], k=5) \
        + random.sample(bingo_numbers[4], k=5)
    boards.append(get_board(arr))
    sanitycheck.add(','.join(map(str, arr)))

assert len(sanitycheck) == num_boards_to_gen

html = get_html(boards)

print(html)
